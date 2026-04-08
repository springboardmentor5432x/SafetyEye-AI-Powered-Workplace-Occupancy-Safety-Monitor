"""
SafetyEye AI -- Fixed Version
Fixes:
  - Webcam video now displays correctly on screen
  - Uploaded video loops continuously and streams frames
  - CCTV / RTSP streams work reliably
  - Alert frames saved and served from /alerts/<filename>
  - Alert log shows saved frame thumbnails in browser

Install:
    pip install flask flask-socketio ultralytics opencv-python

Run:
    python realtime_pipeline.py
    Open http://localhost:5000
"""

import cv2
import time
import threading
import os
import math
import uuid
import base64
from datetime import datetime
from flask import Flask, Response, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from ultralytics import YOLO
from werkzeug.utils import secure_filename

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
MODEL_PATH      = "best_largemodel.pt"
ALERT_SAVE_DIR  = "runs/alerts"
UPLOAD_DIR      = "runs/uploads"
CONF_THRESH     = 0.30
IOU_THRESH      = 0.40
IMG_SIZE        = 640
FRAME_SKIP      = 1
DASHBOARD_PORT  = 5000
ALERT_REPEAT_COOLDOWN_SEC = 8
PERSON_CONF_THRESH = 0.65
PERSON_MIN_AREA_RATIO = 0.03
PERSON_MAX_AREA_RATIO = 0.85

CLASS_NAMES = {
    0:"Hardhat", 1:"Mask", 2:"NO-Hardhat", 3:"NO-Mask",
    4:"NO-Safety Vest", 5:"Person", 6:"Safety Cone",
    7:"Safety Vest", 8:"machinery", 9:"vehicle",
}
VIOLATION_CLASSES  = {2:"NO HARDHAT", 3:"NO MASK", 4:"NO SAFETY VEST"}
BOX_COLORS = {
    0:(0,255,0), 1:(0,200,100), 7:(144,238,144),
    2:(0,0,255), 3:(0,0,180),  4:(0,69,255),
    5:(0,165,255), 6:(255,255,0), 8:(255,0,255), 9:(255,100,0),
}
REQUIRED_PPE       = {"Hardhat":0, "Mask":1, "Safety Vest":7}
MISSING_PPE_LABEL  = {"Hardhat":"NO HARDHAT","Mask":"NO MASK","Safety Vest":"NO SAFETY VEST"}
COLOR_COMPLIANT    = (0,255,0)
COLOR_VIOLATION    = (0,0,255)

os.makedirs(ALERT_SAVE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR,     exist_ok=True)

# ─────────────────────────────────────────────────────────────
# FLASK / SOCKETIO
# ─────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"]         = "safetyeye-ai"
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024
sio = SocketIO(app, async_mode="threading", cors_allowed_origins="*",
               max_http_buffer_size=10*1024*1024)

# ─────────────────────────────────────────────────────────────
# GLOBAL STATE
# ─────────────────────────────────────────────────────────────
pipeline = {
    "running":    False,
    "thread":     None,
    "stop_event": None,
    "jpeg":       None,
    "jpeg_lock":  threading.Lock(),
    "active_violations":        set(),
    "webcam_active_violations": set(),
    "stats": {"fps":0.0,"frame":0,"violations":0,"violation_list":[],"total_alerts":0},
    "alert_log": [],
    "last_alert_time": {},
}
_model = None

# ─────────────────────────────────────────────────────────────
# DRAW HELPERS
# ─────────────────────────────────────────────────────────────

def draw_label(frame, text, x, y, bg, fg=(255,255,255), fs=0.5):
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw,th),bl = cv2.getTextSize(text,font,fs,1)
    p = 5
    cv2.rectangle(frame,(x,y-th-p*2),(x+tw+p*2,y+bl),bg,-1)
    cv2.rectangle(frame,(x,y-th-p*2),(x+tw+p*2,y+bl),(255,255,255),1)
    cv2.putText(frame,text,(x+p,y-p),font,fs,fg,1,cv2.LINE_AA)

def draw_box(frame,box,cid,conf):
    x1,y1,x2,y2 = map(int,box)
    c = BOX_COLORS.get(cid,(200,200,200))
    draw_label(frame,f"{CLASS_NAMES.get(cid,str(cid))}  {conf*100:.0f}%",x1,y1,c,(0,0,0),0.45)
    cv2.rectangle(frame,(x1,y1),(x2,y2),c,2)

def draw_person_box(frame,pbox,pconf,missing,present):
    x1,y1,x2,y2 = map(int,pbox)
    color = COLOR_COMPLIANT if not missing else COLOR_VIOLATION
    cv2.rectangle(frame,(x1,y1),(x2,y2),color,3)
    clen,ct = 15,4
    for (cx,cy) in [(x1,y1),(x2,y1),(x1,y2),(x2,y2)]:
        dx = clen if cx==x1 else -clen
        dy = clen if cy==y1 else -clen
        cv2.line(frame,(cx,cy),(cx+dx,cy),color,ct)
        cv2.line(frame,(cx,cy),(cx,cy+dy),color,ct)
    status = "OK" if not missing else "VIOLATION"
    draw_label(frame,f"Person  {pconf*100:.0f}%  [{status}]",x1,y1,color,(0,0,0),0.5)
    for i,n in enumerate(missing):
        draw_label(frame,f"  MISSING: {n}  ",x1+4,y1+28+i*24,(0,0,200),(255,255,255),0.45)
    for i,n in enumerate(present):
        draw_label(frame,f"  {n}  ",x1+4,y1+28+(len(missing)+i)*24,(0,160,0),(255,255,255),0.45)

def draw_hud(frame,fps,fidx,vcount,talerts):
    h,w = frame.shape[:2]
    ov = frame.copy()
    cv2.rectangle(ov,(0,0),(w,44),(10,10,10),-1)
    cv2.addWeighted(ov,0.75,frame,0.25,0,frame)
    cv2.putText(frame,"SafetyEye AI",(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,220,255),2,cv2.LINE_AA)
    s = f"Frame {fidx}   FPS {fps:.1f}   Violations {vcount}   Alerts {talerts}"
    (tw,_),_ = cv2.getTextSize(s,cv2.FONT_HERSHEY_SIMPLEX,0.48,1)
    cv2.putText(frame,s,(w-tw-10,30),cv2.FONT_HERSHEY_SIMPLEX,0.48,(200,200,200),1,cv2.LINE_AA)
    cv2.line(frame,(0,44),(w,44),(0,200,0) if vcount==0 else (0,0,220),2)

def draw_banner(frame,entries):
    if not entries: return
    h,w = frame.shape[:2]
    rh,p = 36,8
    bh = rh*len(entries)+p*2
    ov = frame.copy()
    cv2.rectangle(ov,(0,h-bh),(w,h),(0,0,140),-1)
    cv2.addWeighted(ov,0.85,frame,0.15,0,frame)
    cv2.line(frame,(0,h-bh),(w,h-bh),(0,0,255),2)
    for i,(name,conf) in enumerate(entries):
        y = h-bh+p+rh*i+rh//2+6
        cv2.rectangle(frame,(8,y-18),(38,y+6),(0,0,255),-1)
        cv2.putText(frame,"!!",(12,y),cv2.FONT_HERSHEY_SIMPLEX,0.55,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(frame,name,(48,y),cv2.FONT_HERSHEY_SIMPLEX,0.62,(255,255,255),2,cv2.LINE_AA)
        pct = f"{conf*100:.1f}%"
        (tw,_),_ = cv2.getTextSize(pct,cv2.FONT_HERSHEY_SIMPLEX,0.62,2)
        cv2.putText(frame,pct,(w-tw-12,y),cv2.FONT_HERSHEY_SIMPLEX,0.62,(255,220,0),2,cv2.LINE_AA)

# ─────────────────────────────────────────────────────────────
# PPE ASSIGNMENT
# ─────────────────────────────────────────────────────────────

def box_center(b): return ((b[0]+b[2])/2,(b[1]+b[3])/2)
def cdist(a,b):
    ax,ay=box_center(a); bx,by=box_center(b)
    return math.hypot(ax-bx,ay-by)
def expand(b,px=60): return [b[0]-px,b[1]-px,b[2]+px,b[3]+px]

def assign_ppe(persons,ppe_items):
    res = {i:{n:False for n in REQUIRED_PPE} for i in range(len(persons))}
    if not persons: return res
    for (pc,_,pb) in ppe_items:
        mn = next((n for n,c in REQUIRED_PPE.items() if c==pc),None)
        if mn is None: continue
        bi,bd = None,float("inf")
        for i,(_,pbox) in enumerate(persons):
            d = cdist(pb,expand(pbox))
            if d<bd: bd=d; bi=i
        if bi is not None: res[bi][mn]=True
    return res

# ─────────────────────────────────────────────────────────────
# RULE ENGINE
# ─────────────────────────────────────────────────────────────

def rule_engine(detections,frame):
    fh, fw = frame.shape[:2]
    frame_area = max(1, fh * fw)

    # Keep only likely real people; suppress common object false positives.
    persons = []
    for (cid, conf, box) in detections:
        if cid != 5:
            continue
        x1, y1, x2, y2 = box
        bw = max(1.0, x2 - x1)
        bh = max(1.0, y2 - y1)
        area_ratio = (bw * bh) / frame_area
        aspect = bh / bw
        if conf < PERSON_CONF_THRESH:
            continue
        if area_ratio < PERSON_MIN_AREA_RATIO or area_ratio > PERSON_MAX_AREA_RATIO:
            continue
        # Person boxes are usually not extremely flat.
        if aspect < 0.55:
            continue
        persons.append((conf, box))

    # Ignore unrelated objects; only use PPE classes tied to person compliance.
    required_ppe_ids = set(REQUIRED_PPE.values())
    ppe_items = [(cid,c,b) for (cid,c,b) in detections if cid in required_ppe_ids]
    vmap      = {}
    all_cids  = [5 for _ in persons]
    for (cid,c,b) in ppe_items: draw_box(frame,b,cid,c)
    if not persons: return vmap,[]
    ppe_a = assign_ppe(persons,ppe_items)
    rev   = {v:k for k,v in VIOLATION_CLASSES.items()}
    for i,(pc,pb) in enumerate(persons):
        s    = ppe_a[i]
        miss = [n for n,f in s.items() if not f]
        pres = [n for n,f in s.items() if f]
        draw_person_box(frame,pb,pc,miss,pres)
        for n in miss:
            vl = MISSING_PPE_LABEL[n]
            if vl not in vmap or pc>vmap[vl]: vmap[vl]=pc
            vid = rev.get(vl)
            if vid is not None and vid not in all_cids: all_cids.append(vid)
    return vmap,all_cids

# ─────────────────────────────────────────────────────────────
# INFERENCE
# ─────────────────────────────────────────────────────────────

def infer(model,frame):
    res = model.predict(source=frame,conf=CONF_THRESH,iou=IOU_THRESH,
                        imgsz=IMG_SIZE,verbose=False)
    dets=[]
    for r in res:
        for b in r.boxes:
            dets.append((int(b.cls[0]),float(b.conf[0]),b.xyxy[0].tolist()))
    return dets

# ─────────────────────────────────────────────────────────────
# ALERT HELPER — saves frame + emits with image URL
# ─────────────────────────────────────────────────────────────

def fire_alert(cid, conf, frame):
    ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg   = VIOLATION_CLASSES[cid]
    fname = f"alert_{msg.replace(' ','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
    fpath = os.path.join(ALERT_SAVE_DIR, fname)

    # Save the annotated frame to disk
    cv2.imwrite(fpath, frame)

    # Also encode as base64 for instant display in browser (no reload needed)
    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
    img_b64 = ""
    if ok:
        img_b64 = "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode()

    entry = {
        "id":       str(uuid.uuid4()),
        "ts":       ts,
        "msg":      msg,
        "conf":     round(conf * 100, 1),
        "type":     "violation",
        "img_url":  f"/alerts/{fname}",   # served by Flask
        "img_b64":  img_b64,              # instant inline display
    }
    pipeline["alert_log"].append(entry)
    pipeline["stats"]["total_alerts"] = len(pipeline["alert_log"])
    pipeline["last_alert_time"][cid] = time.time()
    sio.emit("new_alert", entry)
    print(f"[ALERT] {ts}  {msg}  ({conf*100:.1f}%)  → {fname}")

# ─────────────────────────────────────────────────────────────
# PIPELINE THREAD — upload video + CCTV + server webcam
# ─────────────────────────────────────────────────────────────

def pipeline_thread(source, stop_event, model):
    # Open capture
    if isinstance(source, int):
        cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(source)
    else:
        cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        sio.emit("pipeline_error", {"msg": f"Cannot open: {source}"}); return

    is_live = isinstance(source, int) or (
        isinstance(source, str) and (source.startswith("http") or source.startswith("rtsp")))

    # Background reader for live sources keeps buffer fresh
    fl = threading.Lock()
    lret, lfr = False, None

    def bg_reader():
        nonlocal lret, lfr
        while not stop_event.is_set():
            r, f = cap.read()
            with fl:
                lret, lfr = r, (f.copy() if f is not None else None)
            if not r:
                time.sleep(0.05)

    if is_live:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        threading.Thread(target=bg_reader, daemon=True).start()
        time.sleep(0.5)  # let buffer fill

    fidx = fps = fps_ctr = 0
    fps_t = time.time()
    last_dets = []
    stop_reason = "Done"

    while not stop_event.is_set():
        # ── Read frame ──────────────────────────────────────
        if is_live:
            with fl:
                ret = lret
                fr  = lfr.copy() if lfr is not None else None
            if fr is None:
                time.sleep(0.02)
                continue
        else:
            ret, fr = cap.read()
            if not ret or fr is None:
                # Uploaded/local video: stop cleanly at end of file.
                stop_reason = "Video completed"
                break

        fidx   += 1
        fps_ctr += 1
        elapsed = time.time() - fps_t
        if elapsed >= 1.0:
            fps     = fps_ctr / elapsed
            fps_ctr = 0
            fps_t   = time.time()

        # ── Inference (every N frames) ───────────────────────
        if FRAME_SKIP == 0 or fidx % (FRAME_SKIP + 1) == 0:
            last_dets = infer(model, fr)

        vmap, all_cids = rule_engine(last_dets, fr)
        ventries       = list(vmap.items())

        # ── Trigger alerts for new violations ────────────────
        cur_v = {c for c in all_cids if c in VIOLATION_CLASSES}
        new_v = cur_v - pipeline["active_violations"]
        for cid in new_v:
            now = time.time()
            last_ts = pipeline["last_alert_time"].get(cid, 0.0)
            if now - last_ts >= ALERT_REPEAT_COOLDOWN_SEC:
                conf = vmap.get(VIOLATION_CLASSES[cid], 0.5)
                fire_alert(cid, conf, fr.copy())
        pipeline["active_violations"] = cur_v

        # ── Overlay HUD + banner ─────────────────────────────
        draw_hud(fr, fps, fidx, len(ventries), pipeline["stats"]["total_alerts"])
        draw_banner(fr, ventries)

        # ── Update stats ─────────────────────────────────────
        pipeline["stats"].update({
            "fps":            round(fps, 1),
            "frame":          fidx,
            "violations":     len(ventries),
            "violation_list": [[n, round(c*100,1)] for n,c in ventries],
        })

        # ── Encode to JPEG for streaming ─────────────────────
        ok, buf = cv2.imencode(".jpg", fr, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ok:
            with pipeline["jpeg_lock"]:
                pipeline["jpeg"] = buf.tobytes()

        # ── Emit stats every 10 frames ───────────────────────
        if fidx % 10 == 0:
            sio.emit("stats", pipeline["stats"])

        # ── Frame rate limiter (max ~30fps) ──────────────────
        time.sleep(0.001)

    cap.release()
    pipeline["running"] = False
    # Push final stats so UI keeps latest alert/count values.
    sio.emit("stats", pipeline["stats"])
    sio.emit("pipeline_stopped", {"reason": stop_reason})

# ─────────────────────────────────────────────────────────────
# FLASK ROUTES
# ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return DASHBOARD_HTML

@app.route("/video_feed")
def video_feed():
    """MJPEG stream for uploaded video and CCTV."""
    def gen():
        while True:
            with pipeline["jpeg_lock"]:
                j = pipeline["jpeg"]
            if j:
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + j + b"\r\n"
            time.sleep(0.033)
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/alerts/<path:filename>")
def serve_alert(filename):
    """Serve saved alert frame images from disk."""
    return send_from_directory(ALERT_SAVE_DIR, filename)

@app.route("/start_cctv", methods=["POST"])
def start_cctv():
    url = (request.json or {}).get("url", "").strip()
    if not url:
        return jsonify({"ok": False, "error": "No URL"})
    _stop()
    _start(url, "cctv")
    return jsonify({"ok": True})

@app.route("/upload_video", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"ok": False, "error": "No file"})
    f    = request.files["video"]
    path = os.path.join(UPLOAD_DIR, secure_filename(f.filename))
    f.save(path)
    _stop()
    _start(path, "upload")
    return jsonify({"ok": True, "filename": f.filename})

@app.route("/start_webcam_backend", methods=["POST"])
def start_webcam_backend():
    _stop()
    _start(0, "server_webcam")
    return jsonify({"ok": True})

@app.route("/process_frame", methods=["POST"])
def process_frame():
    """
    Browser webcam mode:
    Browser sends a base64 JPEG frame → server runs inference →
    returns annotated base64 JPEG back to browser for display.
    """
    import numpy as np
    b64 = (request.json or {}).get("frame", "")
    if not b64:
        return jsonify({"ok": False})

    # Decode base64 → numpy array → OpenCV image
    raw  = base64.b64decode(b64.split(",")[-1])
    arr  = np.frombuffer(raw, np.uint8)
    fr   = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if fr is None:
        return jsonify({"ok": False})

    dets              = infer(_model, fr)
    vmap, all_cids    = rule_engine(dets, fr)
    ventries          = list(vmap.items())

    cur_v = {c for c in all_cids if c in VIOLATION_CLASSES}
    new_v = cur_v - pipeline["webcam_active_violations"]
    for cid in new_v:
        conf = vmap.get(VIOLATION_CLASSES[cid], 0.5)
        fire_alert(cid, conf, fr.copy())
    pipeline["webcam_active_violations"] = cur_v

    draw_hud(fr, 0, 0, len(ventries), pipeline["stats"]["total_alerts"])
    draw_banner(fr, ventries)

    pipeline["stats"].update({
        "violations":     len(ventries),
        "violation_list": [[n, round(c*100,1)] for n,c in ventries],
        "total_alerts":   len(pipeline["alert_log"]),
    })
    sio.emit("stats", pipeline["stats"])

    # Encode annotated frame back to base64
    ok, buf = cv2.imencode(".jpg", fr, [cv2.IMWRITE_JPEG_QUALITY, 80])
    if not ok:
        return jsonify({"ok": False})

    return jsonify({
        "ok":             True,
        "frame":          "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode(),
        "violation_list": [[n, round(c*100,1)] for n,c in ventries],
    })

@app.route("/stop", methods=["POST"])
def stop_route():
    _stop()
    return jsonify({"ok": True})

@app.route("/alert_log")
def get_alert_log():
    return jsonify(pipeline["alert_log"])

@app.route("/alert_photos")
def get_alert_photos():
    return jsonify(list(reversed(pipeline["alert_log"])))

# ─────────────────────────────────────────────────────────────
# PIPELINE CONTROL
# ─────────────────────────────────────────────────────────────

def _stop():
    se = pipeline.get("stop_event")
    if se: se.set()
    t = pipeline.get("thread")
    if t and t.is_alive(): t.join(timeout=3)
    pipeline.update({
        "running": False, "jpeg": None,
        "active_violations": set(),
        "webcam_active_violations": set(),
    })

def _start(source, stype):
    global _model
    if _model is None:
        print("[INFO] Loading model…")
        _model = YOLO(MODEL_PATH)
        print("[INFO] Model ready")
    se = threading.Event()
    t  = threading.Thread(target=pipeline_thread, args=(source, se, _model), daemon=True)
    pipeline.update({"running": True, "stop_event": se, "thread": t})
    t.start()

# ─────────────────────────────────────────────────────────────
# SOCKET EVENTS
# ─────────────────────────────────────────────────────────────

@sio.on("connect")
def on_connect():
    sio.emit("stats", pipeline["stats"])
    # Replay last 50 alerts to newly connected client
    for e in pipeline["alert_log"][-50:]:
        sio.emit("new_alert", e)

# ─────────────────────────────────────────────────────────────
# DASHBOARD HTML — inline, no external template files needed
# ─────────────────────────────────────────────────────────────

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SafetyEye AI</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#080b10;--panel:#0d1117;--panel2:#111820;
  --border:#1a2535;--border2:#243040;
  --accent:#00e5ff;--accent2:#0099cc;
  --danger:#ff1f1f;--danger2:#cc0000;
  --safe:#00ff88;--warn:#ffb700;
  --text:#ccd6e8;--dim:#4a6080;--dimmer:#1e2d40;
  --font:'Rajdhani',sans-serif;--mono:'Share Tech Mono',monospace;
  --r:6px;
}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{height:100%;overflow:hidden;}
body{background:var(--bg);color:var(--text);font-family:var(--font);
  display:grid;grid-template-rows:52px 1fr;grid-template-columns:1fr 380px;height:100vh;}
body::before{content:'';position:fixed;inset:0;
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.025) 2px,rgba(0,0,0,.025) 4px);
  pointer-events:none;z-index:9999;}

header{grid-column:1/-1;background:var(--panel);border-bottom:1px solid var(--border);
  display:flex;align-items:center;padding:0 20px;gap:16px;}
.logo{font-size:20px;font-weight:700;letter-spacing:3px;color:var(--accent);
  text-transform:uppercase;font-family:var(--mono);}
.logo em{color:var(--dim);font-style:normal;}
.tagline{font-size:11px;color:var(--dim);letter-spacing:2px;text-transform:uppercase;}
#gstatus{margin-left:auto;display:flex;align-items:center;gap:8px;
  padding:5px 16px;border-radius:20px;border:1px solid var(--safe);
  background:#051a0f;font-size:12px;font-weight:700;color:var(--safe);
  letter-spacing:1px;transition:all .3s;}
#gstatus.alert{border-color:var(--danger);background:#1a0505;color:var(--danger);
  animation:sp 1s infinite;}
#sdot{width:8px;height:8px;border-radius:50%;background:var(--safe);animation:blink 2s infinite;}
#gstatus.alert #sdot{background:var(--danger);}
@keyframes sp{0%,100%{box-shadow:0 0 0 0 rgba(255,31,31,.5);}50%{box-shadow:0 0 0 8px rgba(255,31,31,0);}}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:.3;}}

main{padding:14px;display:flex;flex-direction:column;gap:10px;overflow:hidden;}

.src-tabs{display:flex;gap:0;border:1px solid var(--border2);border-radius:var(--r);overflow:hidden;flex-shrink:0;}
.stab{flex:1;padding:9px 0;border:none;background:var(--panel2);color:var(--dim);
  font-family:var(--font);font-size:13px;font-weight:600;letter-spacing:1px;
  text-transform:uppercase;cursor:pointer;border-right:1px solid var(--border2);transition:all .2s;}
.stab:last-child{border-right:none;}
.stab:hover{background:var(--border2);color:var(--text);}
.stab.active{background:var(--accent2);color:#fff;}

.cfg{display:none;align-items:center;gap:8px;flex-shrink:0;}
.cfg.on{display:flex;}
.cfg input[type=text]{flex:1;background:var(--panel2);border:1px solid var(--border2);
  border-radius:var(--r);padding:8px 14px;color:var(--text);font-family:var(--mono);font-size:13px;outline:none;}
.cfg input:focus{border-color:var(--accent2);}
.upload-lbl{flex:1;background:var(--panel2);border:2px dashed var(--border2);
  border-radius:var(--r);padding:9px 16px;cursor:pointer;
  display:flex;align-items:center;gap:10px;font-size:13px;color:var(--dim);transition:all .2s;}
.upload-lbl:hover{border-color:var(--accent2);color:var(--accent);}
#ufname{color:var(--accent);font-family:var(--mono);font-size:12px;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:260px;}
.btn{padding:8px 18px;border-radius:var(--r);border:none;cursor:pointer;
  font-family:var(--font);font-size:13px;font-weight:700;letter-spacing:1px;
  text-transform:uppercase;transition:all .2s;white-space:nowrap;}
.btn-go{background:var(--accent);color:#000;}
.btn-go:hover{background:#33eeff;}
.btn-go:disabled{background:var(--dimmer);color:var(--dim);cursor:not-allowed;}
.btn-stop{background:var(--danger2);color:#fff;}
.btn-stop:hover{background:var(--danger);}
.webcam-hint{flex:1;font-size:13px;color:var(--dim);padding:8px 4px;}

/* ── Video display area ── */
.vid-wrap{flex:1;background:#000;border:1px solid var(--border);border-radius:var(--r);
  overflow:hidden;position:relative;min-height:0;}

/* ✅ FIX: Both stream-img and wc-canvas fill the container correctly */
#stream-img{width:100%;height:100%;object-fit:contain;display:none;background:#000;}
#wc-canvas {width:100%;height:100%;object-fit:contain;display:none;background:#000;}
#wc-video  {display:none;}

.placeholder{position:absolute;inset:0;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:12px;color:var(--dimmer);}
.placeholder .ico{font-size:52px;opacity:.35;}
.placeholder p{font-size:13px;letter-spacing:2px;text-transform:uppercase;}
#live-badge{position:absolute;top:10px;left:10px;background:rgba(0,0,0,.75);
  border:1px solid var(--border2);border-radius:4px;padding:4px 10px;
  font-family:var(--mono);font-size:11px;color:var(--accent);display:none;}

.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;flex-shrink:0;}
.sc{background:var(--panel);border:1px solid var(--border);border-radius:var(--r);padding:10px 14px;}
.sc .lbl{font-size:10px;letter-spacing:2px;color:var(--dim);text-transform:uppercase;margin-bottom:2px;}
.sc .val{font-family:var(--mono);font-size:24px;color:var(--accent);line-height:1;}
.sc.d .val{color:var(--danger);}

/* ── Sidebar ── */
aside{background:var(--panel);border-left:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden;}
.aside-hd{padding:12px 16px 10px;border-bottom:1px solid var(--border);
  font-size:10px;letter-spacing:2px;color:var(--dim);text-transform:uppercase;
  display:flex;align-items:center;gap:8px;}
.live-dot{width:6px;height:6px;border-radius:50%;background:var(--safe);animation:blink 2s infinite;}
#active-v{padding:10px;display:flex;flex-direction:column;gap:6px;
  min-height:60px;max-height:140px;overflow-y:auto;}
.vtag{background:#150303;border:1px solid var(--danger2);border-left:3px solid var(--danger);
  border-radius:4px;padding:8px 12px;display:flex;justify-content:space-between;align-items:center;}
.vtag .vn{font-size:13px;font-weight:700;color:var(--danger);letter-spacing:1px;}
.vtag .vc{font-family:var(--mono);font-size:12px;color:var(--warn);}
.no-v{color:var(--safe);font-size:13px;font-weight:700;letter-spacing:1px;text-align:center;padding:14px 0;}

.log-hd{display:flex;align-items:center;justify-content:space-between;
  padding:10px 16px 8px;border-bottom:1px solid var(--border);}
.log-hd span{font-size:10px;letter-spacing:2px;color:var(--dim);text-transform:uppercase;}
.btn-clr{font-size:10px;color:var(--dim);background:none;border:1px solid var(--dimmer);
  border-radius:3px;padding:2px 8px;cursor:pointer;font-family:var(--font);}
.btn-clr:hover{color:var(--text);}
.btn-alerts{font-size:10px;color:var(--accent);background:none;border:1px solid var(--accent2);
  border-radius:3px;padding:2px 8px;cursor:pointer;font-family:var(--font);margin-right:6px;}
.btn-alerts:hover{color:#fff;background:var(--accent2);}
#alert-log{flex:1;overflow-y:auto;padding:8px;display:flex;flex-direction:column;
  gap:6px;scrollbar-width:thin;scrollbar-color:var(--border) transparent;}

/* ✅ Alert card with thumbnail image */
.le{border-radius:6px;border-left:3px solid var(--danger);background:#120205;
  animation:fi .4s ease;overflow:hidden;}
.le-top{padding:8px 10px;}
.le .lt{font-family:var(--mono);font-size:10px;color:var(--dim);}
.le .lm{font-size:13px;font-weight:600;color:#ff6060;margin:2px 0 0;}
.le .lc{font-family:var(--mono);font-size:11px;color:var(--warn);}
.le-img{width:100%;max-height:120px;object-fit:cover;display:block;
  border-top:1px solid rgba(255,31,31,0.2);cursor:pointer;}
.le-img:hover{opacity:0.85;}

/* Full-screen image viewer */
#img-viewer{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.92);
  z-index:10010;align-items:center;justify-content:center;cursor:zoom-out;}
#img-viewer.open{display:flex;}
#img-viewer img{max-width:92vw;max-height:92vh;border-radius:4px;
  box-shadow:0 0 60px rgba(0,0,0,0.8);}
#alerts-modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.88);z-index:10001;}
#alerts-modal.open{display:flex;align-items:center;justify-content:center;}
.alerts-panel{width:min(1100px,94vw);height:min(84vh,860px);background:#0b1017;border:1px solid var(--border2);
  border-radius:8px;display:flex;flex-direction:column;overflow:hidden;}
.alerts-head{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;border-bottom:1px solid var(--border2);}
.alerts-title{font-family:var(--mono);letter-spacing:1px;color:var(--accent);}
.alerts-grid{padding:12px;display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px;overflow:auto;}
.acard{background:#121a24;border:1px solid var(--border2);border-radius:6px;overflow:hidden;}
.acard img{width:100%;height:150px;object-fit:cover;display:block;cursor:pointer;}
.ac-body{padding:8px;}
.ac-ts{font-family:var(--mono);font-size:10px;color:var(--dim);}
.ac-msg{font-size:12px;color:#ff7070;font-weight:700;margin-top:4px;}
.ac-conf{font-family:var(--mono);font-size:11px;color:var(--warn);margin-top:3px;}

#afl{position:fixed;inset:0;background:rgba(255,0,0,0);pointer-events:none;z-index:1000;transition:background .1s;}
#afl.flash{background:rgba(255,0,0,.18);}

@keyframes fi{from{opacity:0;transform:translateY(-4px);}to{opacity:1;transform:translateY(0);}}
</style>
</head>
<body>
<div id="afl"></div>

<!-- Full-screen image viewer for alert frames -->
<div id="img-viewer" onclick="closeViewer()">
  <img id="viewer-img" src="" alt="Alert frame">
</div>
<div id="alerts-modal">
  <div class="alerts-panel">
    <div class="alerts-head">
      <div class="alerts-title">ALERTS TIMELINE</div>
      <button class="btn-clr" onclick="closeAlertsModal()">Close</button>
    </div>
    <div class="alerts-grid" id="alerts-grid"></div>
  </div>
</div>

<header>
  <div class="logo">Safety<em>Eye</em> AI</div>
  <div class="tagline">PPE Compliance Monitor</div>
  <div id="gstatus"><span id="sdot"></span><span id="stxt">STANDBY</span></div>
</header>

<main>
  <div class="src-tabs">
    <button class="stab active" onclick="setMode('upload')">⬆ Upload Video</button>
    <button class="stab"        onclick="setMode('cctv')">📡 CCTV / URL</button>
    <button class="stab"        onclick="setMode('webcam')">🎥 Webcam</button>
  </div>

  <!-- Upload -->
  <div class="cfg on" id="cfg-upload">
    <label class="upload-lbl" for="vfile">
      <span>📁</span><span id="ufname">Choose a video file…</span>
    </label>
    <input type="file" id="vfile" accept="video/*" style="display:none" onchange="onFile(this)">
    <button class="btn btn-go" id="btn-upload" onclick="startUpload()" disabled>Analyse</button>
    <button class="btn btn-stop" onclick="stopAll()">Stop</button>
  </div>

  <!-- CCTV -->
  <div class="cfg" id="cfg-cctv">
    <input type="text" id="cctv-url" placeholder="rtsp://192.168.x.x/stream  or  http://IP:8080/video">
    <button class="btn btn-go" onclick="startCCTV()">Connect</button>
    <button class="btn btn-stop" onclick="stopAll()">Stop</button>
  </div>

  <!-- Webcam -->
  <div class="cfg" id="cfg-webcam">
    <div class="webcam-hint">Browser camera → frames processed by server in real time.</div>
    <button class="btn btn-go" onclick="startWebcam()">Start Browser Cam</button>
    <button class="btn btn-go" onclick="startServerWebcam()">Server Cam</button>
    <button class="btn btn-stop" onclick="stopWebcam()">Stop</button>
  </div>

  <!-- Video area -->
  <div class="vid-wrap">
    <div class="placeholder" id="ph">
      <div class="ico">🛡️</div>
      <p>Select a source to begin monitoring</p>
    </div>
    <!-- MJPEG stream (upload / CCTV / server webcam) -->
    <img id="stream-img" src="" alt="Live stream">
    <!-- Browser webcam canvas -->
    <video id="wc-video" autoplay playsinline muted></video>
    <canvas id="wc-canvas"></canvas>
    <div id="live-badge">● LIVE</div>
  </div>

  <div class="stats">
    <div class="sc"><div class="lbl">FPS</div><div class="val" id="s-fps">—</div></div>
    <div class="sc"><div class="lbl">Frame</div><div class="val" id="s-fr">—</div></div>
    <div class="sc d"><div class="lbl">Active Violations</div><div class="val" id="s-viol">0</div></div>
    <div class="sc"><div class="lbl">Total Alerts</div><div class="val" id="s-al">0</div></div>
  </div>
</main>

<aside>
  <div class="aside-hd"><div class="live-dot"></div>Active Violations</div>
  <div id="active-v"><div class="no-v" id="no-v" style="display:none"></div></div>

  <div class="log-hd">
    <span>Alert Log</span>
    <div>
      <button class="btn-alerts" onclick="openAlertsModal()">Alerts</button>
      <button class="btn-clr" onclick="clearLog()">Clear</button>
    </div>
  </div>
  <div id="alert-log"></div>
</aside>

<script>
const socket = io();
let mode='upload', wcStream=null, wcTimer=null, chosenFile=null;
let audioCtx=null;

// ── Image viewer ─────────────────────────────────────────────
function openViewer(src){
  const viewer = document.getElementById('img-viewer');
  document.getElementById('viewer-img').src = src;
  viewer.style.zIndex = '10010';
  viewer.classList.add('open');
}
function closeViewer()  { document.getElementById('img-viewer').classList.remove('open'); }
function closeAlertsModal(){ document.getElementById('alerts-modal').classList.remove('open'); }
function openAlertsModal(){
  const grid=document.getElementById('alerts-grid');
  grid.innerHTML='<div class="ac-ts">Loading...</div>';
  fetch('/alert_photos')
    .then(r=>r.json())
    .then(items=>{
      grid.innerHTML='';
      if(!items.length){
        grid.innerHTML='<div class="ac-ts">No alerts captured yet.</div>';
        return;
      }
      items.forEach(e=>{
        const src=e.img_url || e.img_b64 || '';
        const card=document.createElement('div');
        card.className='acard';
        card.innerHTML=`<img src="${src}" alt="Alert frame" onclick="openViewer('${src}')">
          <div class="ac-body">
            <div class="ac-ts">${e.ts || ''}</div>
            <div class="ac-msg">${e.msg || 'ALERT'}</div>
            <div class="ac-conf">Confidence: ${e.conf || 0}%</div>
          </div>`;
        grid.appendChild(card);
      });
    })
    .catch(()=>{ grid.innerHTML='<div class="ac-ts">Failed to load alerts.</div>'; });
  document.getElementById('alerts-modal').classList.add('open');
}

// ── Mode switcher ─────────────────────────────────────────────
function setMode(m){
  mode=m;
  document.querySelectorAll('.stab').forEach((b,i)=>{
    b.classList.toggle('active',['upload','cctv','webcam'][i]===m);
  });
  document.querySelectorAll('.cfg').forEach(c=>c.classList.remove('on'));
  document.getElementById('cfg-'+m).classList.add('on');
}

// ── Upload ────────────────────────────────────────────────────
function onFile(inp){
  if(!inp.files.length)return;
  chosenFile=inp.files[0];
  document.getElementById('ufname').textContent=chosenFile.name;
  document.getElementById('btn-upload').disabled=false;
}
function startUpload(){
  if(!chosenFile)return;
  showServerStream();
  const fd=new FormData(); fd.append('video',chosenFile);
  fetch('/upload_video',{method:'POST',body:fd})
    .then(r=>r.json()).then(d=>{if(!d.ok)alert('Upload error: '+d.error);});
}

// ── CCTV ──────────────────────────────────────────────────────
function startCCTV(){
  const url=document.getElementById('cctv-url').value.trim();
  if(!url){alert('Enter a stream URL');return;}
  showServerStream();
  fetch('/start_cctv',{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({url})
  }).then(r=>r.json()).then(d=>{if(!d.ok)alert('CCTV error: '+d.error);});
}

// ── Browser webcam ────────────────────────────────────────────
async function startWebcam(){
  try{
    if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia)
      throw new Error('Camera API unavailable');

    wcStream = await navigator.mediaDevices.getUserMedia({
      video:{width:{ideal:640},height:{ideal:480},facingMode:'environment'}
    });

    const vid = document.getElementById('wc-video');
    vid.srcObject = wcStream;

    // ✅ FIX: wait for metadata so we know the actual video dimensions
    await new Promise(res => {
      if(vid.readyState >= 1){ res(); return; }
      vid.addEventListener('loadedmetadata', res, {once:true});
    });
    await vid.play();

    // ✅ FIX: set canvas to actual video dimensions
    const c = document.getElementById('wc-canvas');
    c.width  = vid.videoWidth  || 640;
    c.height = vid.videoHeight || 480;

    showWebcamStream();

    // ✅ FIX: send frames every 200ms and draw annotated result back
    wcTimer = setInterval(sendFrame, 200);

  }catch(e){
    console.warn('Browser webcam failed:', e.message);
    alert('Camera error: '+e.message+'. Trying server webcam instead.');
    startServerWebcam();
  }
}

function startServerWebcam(){
  showServerStream();
  fetch('/start_webcam_backend',{method:'POST'})
    .then(r=>r.json())
    .then(d=>{ if(!d.ok) alert('Server webcam failed to open'); })
    .catch(()=>alert('Server webcam error'));
}

function stopWebcam(){
  if(wcTimer){ clearInterval(wcTimer); wcTimer=null; }
  if(wcStream){ wcStream.getTracks().forEach(t=>t.stop()); wcStream=null; }
  hideStream();
  fetch('/stop',{method:'POST'});
}

function sendFrame(){
  const vid = document.getElementById('wc-video');
  if(!vid.videoWidth) return; // video not ready yet

  // Draw current video frame to temp canvas
  const tmp = document.createElement('canvas');
  tmp.width  = vid.videoWidth;
  tmp.height = vid.videoHeight;
  tmp.getContext('2d').drawImage(vid, 0, 0);

  const b64 = tmp.toDataURL('image/jpeg', 0.75);

  fetch('/process_frame',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({frame: b64})
  })
  .then(r=>r.json())
  .then(d=>{
    if(!d.ok || !d.frame) return;

    // ✅ FIX: draw annotated frame onto the visible canvas
    const c   = document.getElementById('wc-canvas');
    const ctx = c.getContext('2d');
    const img = new Image();
    img.onload = () => {
      // Resize canvas if needed
      if(c.width !== img.naturalWidth)  c.width  = img.naturalWidth;
      if(c.height !== img.naturalHeight) c.height = img.naturalHeight;
      ctx.drawImage(img, 0, 0);
    };
    img.src = d.frame;
  })
  .catch(()=>{});
}

// ── Stop all ──────────────────────────────────────────────────
function stopAll(){
  if(wcTimer){ clearInterval(wcTimer); wcTimer=null; }
  if(wcStream){ wcStream.getTracks().forEach(t=>t.stop()); wcStream=null; }
  hideStream();
  fetch('/stop',{method:'POST'});
}

// ── Display helpers ───────────────────────────────────────────
function showServerStream(){
  document.getElementById('ph').style.display='none';
  document.getElementById('live-badge').style.display='block';
  // Add cache-busting timestamp to force browser to reload the stream
  document.getElementById('stream-img').src = '/video_feed?t='+Date.now();
  document.getElementById('stream-img').style.display='block';
  document.getElementById('wc-canvas').style.display='none';
}
function showWebcamStream(){
  document.getElementById('ph').style.display='none';
  document.getElementById('live-badge').style.display='block';
  document.getElementById('wc-canvas').style.display='block';
  document.getElementById('stream-img').style.display='none';
}
function hideStream(){
  document.getElementById('stream-img').style.display='none';
  document.getElementById('wc-canvas').style.display='none';
  document.getElementById('live-badge').style.display='none';
  document.getElementById('ph').style.display='flex';
  document.getElementById('stream-img').src='';
}

// ── Socket: stats ─────────────────────────────────────────────
socket.on('stats', d=>{
  document.getElementById('s-fps').textContent  = (d.fps||0).toFixed(1);
  document.getElementById('s-fr').textContent   = d.frame || '—';
  document.getElementById('s-viol').textContent = d.violations || 0;
  document.getElementById('s-al').textContent   = d.total_alerts || 0;

  const gs=document.getElementById('gstatus'), tx=document.getElementById('stxt');
  if((d.violations||0)>0){ gs.classList.add('alert');    tx.textContent='VIOLATION DETECTED'; }
  else                    { gs.classList.remove('alert'); tx.textContent='MONITORING'; }

  const av=document.getElementById('active-v'), nv=document.getElementById('no-v');
  av.querySelectorAll('.vtag').forEach(e=>e.remove());
  if(d.violation_list && d.violation_list.length){
    nv.style.display='none';
    d.violation_list.forEach(([n,c])=>{
      const t=document.createElement('div'); t.className='vtag';
      t.innerHTML=`<span class="vn">${n}</span><span class="vc">${c}%</span>`;
      av.appendChild(t);
    });
  } else { nv.style.display='none'; }
});

// ── Socket: new alert — shows frame thumbnail ─────────────────
socket.on('new_alert', entry=>{
  prependLog(entry);
  // Keep alerts in log only; avoid intrusive per-frame feedback.
});

socket.on('pipeline_stopped', ()=>{
  document.getElementById('stxt').textContent='STOPPED';
  document.getElementById('gstatus').classList.remove('alert');
});
socket.on('pipeline_error', e=>{
  document.getElementById('stxt').textContent='ERROR';
  document.getElementById('gstatus').classList.add('alert');
  alert('Pipeline error: '+(e&&e.msg?e.msg:'Unknown'));
});

// ✅ Alert card with thumbnail image
function prependLog(e){
  const log = document.getElementById('alert-log');
  const el  = document.createElement('div');
  el.className='le';

  // Use base64 for instant display, fallback to URL
  const imgSrc = e.img_b64 || e.img_url || '';
  const imgHtml = imgSrc
    ? `<img class="le-img" src="${imgSrc}" alt="Alert frame"
         onclick="openViewer('${e.img_url || imgSrc}')"
         title="Click to view full size">`
    : '';

  el.innerHTML=`
    <div class="le-top">
      <div class="lt">${e.ts}</div>
      <div class="lm">⚠ ${e.msg}</div>
      <div class="lc">Confidence: ${e.conf}%</div>
    </div>
    ${imgHtml}`;
  log.prepend(el);
  // Keep max 200 alert cards in DOM
  while(log.children.length > 200) log.removeChild(log.lastChild);
}

function flashScreen(){
  const f=document.getElementById('afl');
  f.classList.add('flash');
  setTimeout(()=>f.classList.remove('flash'),400);
}
function beep(){
  try{
    if(!audioCtx) audioCtx=new(window.AudioContext||window.webkitAudioContext)();
    const o=audioCtx.createOscillator(), g=audioCtx.createGain();
    o.connect(g); g.connect(audioCtx.destination);
    o.frequency.setValueAtTime(900, audioCtx.currentTime);
    o.frequency.exponentialRampToValueAtTime(400, audioCtx.currentTime+0.18);
    g.gain.setValueAtTime(0.3, audioCtx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime+0.35);
    o.start(); o.stop(audioCtx.currentTime+0.35);
  }catch(e){}
}
function clearLog(){ document.getElementById('alert-log').innerHTML=''; }
</script>
</body>
</html>"""

# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="SafetyEye AI Web Pipeline")
    p.add_argument("--port", type=int, default=DASHBOARD_PORT)
    args = p.parse_args()

    print("[INFO] Loading YOLOv8 model…")
    _model = YOLO(MODEL_PATH)
    print(f"[INFO] Model ready")
    print(f"[INFO] Dashboard → http://localhost:{args.port}")
    sio.run(app, host="0.0.0.0", port=args.port, allow_unsafe_werkzeug=True)