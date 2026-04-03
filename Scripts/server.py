# --- imports remain same ---
import asyncio
import json
import threading
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from alerter import Alerter
from detector import Detector, ViolationEvent
from logger import SafetyLogger


# --- CONFIG ---
base = Path(__file__).parent.parent
MODEL_PATH = base / "Models" / "secondbest.pt"

# VIDEO_SOURCE = 0
VIDEO_SOURCE = base / "video"/ "10202777-hd_3842_2160_30fps (1).mp4"
CONFIDENCE = 0.50
RESOLUTION = (640, 480)
LOG_DIR = "logs"


# --- STATE ---
detector: Optional[Detector] = None
alerter = Alerter()
safety_logger = SafetyLogger(LOG_DIR)

event_queue: List[ViolationEvent] = []
event_clients: List[WebSocket] = []
stream_clients: List[WebSocket] = []

clients_lock = threading.Lock()

stream_mode = "backend"  # "backend" or "frontend"


# --- LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global detector

    detector = Detector(
        model_path=MODEL_PATH,
        webcam_index=None,
        confidence=CONFIDENCE,
        resolution=RESOLUTION,
    )

    asyncio.create_task(process_events())
    asyncio.create_task(video_stream_loop())

    yield


# --- APP ---
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- MODELS ---
class AlertOut(BaseModel):
    violation_type: str
    detected_at: str
    escalated: bool
    acknowledged: bool


class AcknowledgeRequest(BaseModel):
    violation_type: str


class LogExcerptOut(BaseModel):
    lines: str
    log_dir: str


# =========================================================
# 🔥 BACKEND VIDEO STREAM LOOP (MAIN FIX)
# =========================================================
async def video_stream_loop():
    cap = cv2.VideoCapture(VIDEO_SOURCE)

    last_processed = None
    frame_count = 0

    while True:
        await asyncio.sleep(0.03)  # ~30 FPS

        if stream_mode != "backend":
            continue

        ret, frame = cap.read()
        if not ret:
            cap.release()
            cap = cv2.VideoCapture(VIDEO_SOURCE)
            last_processed = None
            frame_count = 0
            continue

        frame_count += 1

        if frame_count % 3 != 0 and last_processed is not None:
            payload = last_processed
        else:
            small = cv2.resize(frame, (320, 240))
            processed_small, events = detector.process_frame(small)
            processed = cv2.resize(processed_small, (frame.shape[1], frame.shape[0]))

            for event in events:
                with clients_lock:
                    event_queue.append(event)

            _, buf = cv2.imencode(".jpg", processed, [cv2.IMWRITE_JPEG_QUALITY, 55])
            payload = buf.tobytes()
            last_processed = payload

        dead = []
        for ws in list(stream_clients):
            try:
                await ws.send_bytes(payload)
            except:
                dead.append(ws)

        for ws in dead:
            stream_clients.remove(ws)


# =========================================================
# 🔥 EVENT STREAM
# =========================================================
async def process_events():
    while True:
        await asyncio.sleep(0.1)

        with clients_lock:
            events = list(event_queue)
            event_queue.clear()

        for event in events:
            payload = json.dumps({
                "type": "violation",
                "violation_type": event.violation_type,
                "confidence": round(event.confidence, 3),
                "timestamp": event.timestamp.isoformat(),
            })

            dead = []
            for ws in list(event_clients):
                try:
                    await ws.send_text(payload)
                except:
                    dead.append(ws)

            for ws in dead:
                event_clients.remove(ws)

        alerter.tick()


# =========================================================
# 🔥 VIDEO SOCKET (CLEANED)
# =========================================================
@app.websocket("/ws/stream")
async def ws_stream(websocket: WebSocket):
    await websocket.accept()
    stream_clients.append(websocket)

    try:
        while True:
            if stream_mode == "frontend":
                frame_bytes = await websocket.receive_bytes()

                np_arr = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if frame is None:
                    continue

                small = cv2.resize(frame, (320, 240))
                processed_small, events = detector.process_frame(small)
                processed = cv2.resize(processed_small, (frame.shape[1], frame.shape[0]))

                for event in events:
                    with clients_lock:
                        event_queue.append(event)

                _, buf = cv2.imencode(".jpg", processed, [cv2.IMWRITE_JPEG_QUALITY, 55])
                await websocket.send_bytes(buf.tobytes())

            else:
                await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        if websocket in stream_clients:
            stream_clients.remove(websocket)


# =========================================================
# 🔥 EVENTS SOCKET
# =========================================================
@app.websocket("/ws/events")
async def ws_events(websocket: WebSocket):
    await websocket.accept()
    event_clients.append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        event_clients.remove(websocket)


# =========================================================
# 🔥 MODE SWITCH
# =========================================================
@app.post("/api/stream-mode/{mode}")
def set_mode(mode: str):
    global stream_mode
    if mode not in ["frontend", "backend"]:
        raise HTTPException(status_code=400, detail="Invalid mode")

    stream_mode = mode
    return {"mode": stream_mode}


# =========================================================
# 🔥 LOGS
# =========================================================
@app.get("/api/logs", response_model=LogExcerptOut)
def get_logs(n: int = 20):
    return LogExcerptOut(
        lines=safety_logger.get_recent_excerpt(n_lines=n),
        log_dir=LOG_DIR,
    )


# =========================================================
# 🔥 ALERTS
# =========================================================
@app.get("/api/alerts", response_model=List[AlertOut])
def get_alerts():
    return [
        AlertOut(
            violation_type=a.violation_type,
            detected_at=a.detected_at.isoformat(),
            escalated=a.escalated,
            acknowledged=a.acknowledged,
        )
        for a in alerter.active_alerts()
    ]


@app.post("/api/alerts/acknowledge")
def acknowledge_alert(body: AcknowledgeRequest):
    alerter.acknowledge(body.violation_type)
    return {"acknowledged": body.violation_type}