"""
SafetyEye AI — Milestone 3
Real-Time PPE Detection via Webcam or Video File
Uses: best_largemodel.pt (YOLOv8 large, 50 epochs, 640px)

Usage:
    python webcam_detect.py                        # webcam (default)
    python webcam_detect.py --source video.mp4     # video file
    python webcam_detect.py --source 0             # explicit webcam index
"""

import cv2
import argparse
import time
from datetime import datetime
from ultralytics import YOLO

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
MODEL_PATH   = "best_largemodel.pt"
CONF_THRESH  = 0.40          # minimum confidence to accept a detection
IOU_THRESH   = 0.45          # NMS IoU threshold
IMG_SIZE     = 640           # must match training resolution
ALERT_COOLDOWN_SEC = 5       # seconds between repeated console alerts per violation type

# Class names (must match your map.yaml order)
CLASS_NAMES = {
    0: "Hardhat",
    1: "Mask",
    2: "NO-Hardhat",
    3: "NO-Mask",
    4: "NO-Safety Vest",
    5: "Person",
    6: "Safety Cone",
    7: "Safety Vest",
    8: "machinery",
    9: "vehicle",
}

# Violation classes (directly detected by your model)
VIOLATION_CLASSES = {
    2: "[!!] NO HARDHAT detected!",
    3: "[!!] NO MASK detected!",
    4: "[!!] NO SAFETY VEST detected!",
}

# Bounding box colors per class (BGR)
BOX_COLORS = {
    0:  (0, 255, 0),     # Hardhat        → green
    1:  (0, 255, 180),   # Mask           → teal
    2:  (0, 0, 255),     # NO-Hardhat     → red
    3:  (0, 0, 220),     # NO-Mask        → dark red
    4:  (0, 60, 255),    # NO-Safety Vest → orange-red
    5:  (255, 200, 0),   # Person         → blue-ish
    6:  (200, 200, 0),   # Safety Cone    → cyan
    7:  (0, 200, 100),   # Safety Vest    → green
    8:  (180, 0, 255),   # Machinery      → purple
    9:  (255, 100, 0),   # Vehicle        → blue
}

DEFAULT_COLOR = (200, 200, 200)


# ─────────────────────────────────────────────
# ALERT SYSTEM (Console + Visual Overlay)
# ─────────────────────────────────────────────
class AlertSystem:
    def __init__(self, cooldown_sec=ALERT_COOLDOWN_SEC):
        self.cooldown = cooldown_sec
        self.last_alert_time = {}   # violation_class_id → last alert timestamp
        self.violation_log = []     # full log of all alerts

    def trigger(self, class_id: int):
        """Fire a console alert for a violation class, respecting cooldown."""
        now = time.time()
        last = self.last_alert_time.get(class_id, 0)

        if now - last >= self.cooldown:
            self.last_alert_time[class_id] = now
            msg = VIOLATION_CLASSES[class_id]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_msg = f"[{timestamp}] SAFETY ALERT -- {msg}"
            print(full_msg)
            self.violation_log.append(full_msg)

    def get_active_violations(self, detected_class_ids: list) -> list:
        """Return list of active violation class ids from current detections."""
        return [cid for cid in detected_class_ids if cid in VIOLATION_CLASSES]


# ─────────────────────────────────────────────
# DRAW UTILITIES
# ─────────────────────────────────────────────
def draw_detection(frame, box, class_id, conf):
    """Draw bounding box + label on frame."""
    x1, y1, x2, y2 = map(int, box)
    color = BOX_COLORS.get(class_id, DEFAULT_COLOR)
    label = f"{CLASS_NAMES.get(class_id, str(class_id))} {conf:.2f}"

    # Box
    thickness = 2 if class_id not in VIOLATION_CLASSES else 3
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

    # Label background
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
    cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)

    # Label text
    cv2.putText(frame, label, (x1 + 2, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)


def draw_status_bar(frame, fps, violation_count, total_violations_logged):
    """Draw a HUD bar at top of frame."""
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (w, 36), (20, 20, 20), -1)

    status = f"SafetyEye AI  |  FPS: {fps:.1f}  |  Violations this frame: {violation_count}  |  Total alerts: {total_violations_logged}"
    cv2.putText(frame, status, (8, 24),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 230, 255), 1, cv2.LINE_AA)


def draw_violation_banner(frame, active_violations):
    """Draw red violation banner at bottom of frame."""
    if not active_violations:
        return
    h, w = frame.shape[:2]
    banner_h = 32 * len(active_violations) + 10
    cv2.rectangle(frame, (0, h - banner_h), (w, h), (0, 0, 180), -1)

    for i, cid in enumerate(active_violations):
        text = f"  {VIOLATION_CLASSES[cid]}"
        cv2.putText(frame, text, (8, h - banner_h + 26 + i * 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)


# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────
def run(source):
    print(f"\n{'='*55}")
    print("  SafetyEye AI — Real-Time Detection (Milestone 3)")
    print(f"{'='*55}")
    print(f"  Model   : {MODEL_PATH}")
    print(f"  Source  : {source}")
    print(f"  Conf    : {CONF_THRESH}   |   IOU: {IOU_THRESH}")
    print(f"{'='*55}\n")
    print("  Press  Q  to quit.\n")

    # Load model
    model = YOLO(MODEL_PATH)
    print(f"[INFO] Model loaded — classes: {model.names}\n")

    # Open video source
    cap_source = 0 if source == "0" else source
    cap = cv2.VideoCapture(cap_source)

    if not cap.isOpened():
        print(f"[ERROR] Cannot open source: {source}")
        return

    alert_system = AlertSystem()
    fps_timer = time.time()
    frame_count = 0
    fps = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[INFO] Stream ended or frame unreadable.")
            break

        frame_count += 1

        # ── FPS calculation ──────────────────
        elapsed = time.time() - fps_timer
        if elapsed >= 1.0:
            fps = frame_count / elapsed
            frame_count = 0
            fps_timer = time.time()

        # ── YOLOv8 Inference ────────────────
        results = model.predict(
            source=frame,
            conf=CONF_THRESH,
            iou=IOU_THRESH,
            imgsz=IMG_SIZE,
            verbose=False,
            device="0" if _gpu_available() else "cpu",
        )

        # ── Parse detections ────────────────
        detected_class_ids = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                conf     = float(box.conf[0])
                coords   = box.xyxy[0].tolist()

                detected_class_ids.append(class_id)
                draw_detection(frame, coords, class_id, conf)

        # ── Violation logic ─────────────────
        active_violations = alert_system.get_active_violations(detected_class_ids)

        for cid in active_violations:
            alert_system.trigger(cid)

        # ── Visual overlays ──────────────────
        draw_status_bar(frame, fps, len(active_violations), len(alert_system.violation_log))
        draw_violation_banner(frame, active_violations)

        # ── Show frame ───────────────────────
        cv2.imshow("SafetyEye AI — Real-Time Detection (Q to quit)", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("\n[INFO] User quit.")
            break

    cap.release()
    cv2.destroyAllWindows()

    # ── Session summary ──────────────────────
    print(f"\n{'='*55}")
    print("  Session Summary")
    print(f"{'='*55}")
    print(f"  Total alerts fired : {len(alert_system.violation_log)}")
    if alert_system.violation_log:
        print("\n  Alert log:")
        for entry in alert_system.violation_log:
            print(f"    {entry}")
    print(f"{'='*55}\n")


def _gpu_available():
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SafetyEye AI — Real-Time Detection")
    parser.add_argument("--source", type=str, default="0",
                        help="Video source: 0 for webcam, or path to video file")
    args = parser.parse_args()
    run(args.source)