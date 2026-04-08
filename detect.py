"""
SafetyEye AI — Milestone 3
Offline Detection Script (images / video files / folders)
Uses: best_largemodel.pt

Usage:
    python detect.py --source test.jpg
    python detect.py --source datasets/images/val
    python detect.py --source footage.mp4
    python detect.py --source test.jpg --save          # save annotated output
"""

import cv2
import argparse
import os
import time
from datetime import datetime
from pathlib import Path
from ultralytics import YOLO

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
MODEL_PATH  = "best_largemodel.pt"
CONF_THRESH = 0.40
IOU_THRESH  = 0.45
IMG_SIZE    = 640
OUTPUT_DIR  = "runs/detect/safetyeye_output"

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

VIOLATION_CLASSES = {2, 3, 4}   # classes that represent a PPE violation

BOX_COLORS = {
    0:  (0, 255, 0),
    1:  (0, 255, 180),
    2:  (0, 0, 255),
    3:  (0, 0, 220),
    4:  (0, 60, 255),
    5:  (255, 200, 0),
    6:  (200, 200, 0),
    7:  (0, 200, 100),
    8:  (180, 0, 255),
    9:  (255, 100, 0),
}

VIOLATION_MESSAGES = {
    2: "NO HARDHAT",
    3: "NO MASK",
    4: "NO SAFETY VEST",
}

DEFAULT_COLOR = (200, 200, 200)
IMAGE_EXTS    = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_EXTS    = {".mp4", ".avi", ".mov", ".mkv"}


# ─────────────────────────────────────────────
# DRAW UTILITIES
# ─────────────────────────────────────────────
def draw_detection(frame, box, class_id, conf):
    x1, y1, x2, y2 = map(int, box)
    color = BOX_COLORS.get(class_id, DEFAULT_COLOR)
    label = f"{CLASS_NAMES.get(class_id, str(class_id))} {conf:.2f}"

    thickness = 3 if class_id in VIOLATION_CLASSES else 2
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
    cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
    cv2.putText(frame, label, (x1 + 2, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)


def draw_violation_overlay(frame, violations_in_frame):
    """Stamp violation warnings onto the frame."""
    if not violations_in_frame:
        return
    h, w = frame.shape[:2]
    banner_h = 32 * len(violations_in_frame) + 10
    cv2.rectangle(frame, (0, h - banner_h), (w, h), (0, 0, 160), -1)
    for i, msg in enumerate(violations_in_frame):
        cv2.putText(frame, f"  [!] {msg}", (8, h - banner_h + 26 + i * 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)


# ─────────────────────────────────────────────
# CONSOLE ALERT
# ─────────────────────────────────────────────
def console_alert(source_name: str, violations: list):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for v in violations:
        print(f"[{ts}] SAFETY ALERT [{source_name}] -- {v}")


# ─────────────────────────────────────────────
# PROCESS SINGLE IMAGE
# ─────────────────────────────────────────────
def process_image(model, image_path: str, save: bool) -> dict:
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"[WARN] Cannot read image: {image_path}")
        return {}

    results = model.predict(
        source=frame, conf=CONF_THRESH, iou=IOU_THRESH,
        imgsz=IMG_SIZE, verbose=False
    )

    violations_found = []
    detection_summary = []

    for result in results:
        for box in result.boxes:
            cid   = int(box.cls[0])
            conf  = float(box.conf[0])
            coords = box.xyxy[0].tolist()
            draw_detection(frame, coords, cid, conf)
            detection_summary.append((CLASS_NAMES.get(cid, str(cid)), conf))
            if cid in VIOLATION_CLASSES:
                violations_found.append(VIOLATION_MESSAGES[cid])

    draw_violation_overlay(frame, violations_found)

    # Add header bar
    cv2.rectangle(frame, (0, 0), (frame.shape[1], 30), (20, 20, 20), -1)
    cv2.putText(frame, f"SafetyEye AI  |  {Path(image_path).name}",
                (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 230, 255), 1)

    # Console alerts
    if violations_found:
        console_alert(Path(image_path).name, violations_found)

    # Always save every annotated image automatically
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"annotated_{Path(image_path).name}")
    cv2.imwrite(out_path, frame)
    print(f"[SAVED] {out_path}")

    return {"file": image_path, "detections": detection_summary, "violations": violations_found}


# ─────────────────────────────────────────────
# PROCESS VIDEO FILE
# ─────────────────────────────────────────────
def process_video(model, video_path: str, save: bool):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open video: {video_path}")
        return

    fps_src = cap.get(cv2.CAP_PROP_FPS) or 25
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    writer = None
    if save:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        out_path = os.path.join(OUTPUT_DIR, f"annotated_{Path(video_path).name}")
        writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), fps_src, (w, h))
        print(f"[INFO] Saving output to: {out_path}")

    total_alerts = 0
    frame_idx = 0
    t_start = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1

        results = model.predict(
            source=frame, conf=CONF_THRESH, iou=IOU_THRESH,
            imgsz=IMG_SIZE, verbose=False
        )

        violations_in_frame = []

        for result in results:
            for box in result.boxes:
                cid    = int(box.cls[0])
                conf   = float(box.conf[0])
                coords = box.xyxy[0].tolist()
                draw_detection(frame, coords, cid, conf)
                if cid in VIOLATION_CLASSES:
                    msg = VIOLATION_MESSAGES[cid]
                    if msg not in violations_in_frame:
                        violations_in_frame.append(msg)

        if violations_in_frame:
            console_alert(f"{Path(video_path).name} frame#{frame_idx}", violations_in_frame)
            total_alerts += len(violations_in_frame)

        draw_violation_overlay(frame, violations_in_frame)

        elapsed = time.time() - t_start
        current_fps = frame_idx / elapsed if elapsed > 0 else 0
        cv2.rectangle(frame, (0, 0), (w, 32), (20, 20, 20), -1)
        cv2.putText(frame,
                    f"SafetyEye AI  |  Frame: {frame_idx}  |  FPS: {current_fps:.1f}  |  Alerts: {total_alerts}",
                    (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 230, 255), 1)

        if writer:
            writer.write(frame)

        cv2.imshow(f"SafetyEye — {Path(video_path).name} (Q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()
    print(f"\n[INFO] Video done. Total violation alerts: {total_alerts}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def run(source: str, save: bool):
    print(f"\n{'='*55}")
    print("  SafetyEye AI — Offline Detection (Milestone 3)")
    print(f"{'='*55}")
    print(f"  Model  : {MODEL_PATH}")
    print(f"  Source : {source}")
    print(f"  Save   : {save}")
    print(f"{'='*55}\n")

    model = YOLO(MODEL_PATH)

    src_path = Path(source).resolve()   # resolve to absolute path
    print(f"[INFO] Resolved path : {src_path}")
    print(f"[INFO] Is directory  : {src_path.is_dir()}")
    print(f"[INFO] Exists        : {src_path.exists()}\n")

    # Use os.path as fallback — more reliable on Windows with relative paths
    is_dir = src_path.is_dir() or os.path.isdir(source)

    # ── Folder of images / videos ────────────
    if is_dir:
        src_path = Path(os.path.abspath(source))  # recompute with os.path.abspath
        files = sorted(src_path.iterdir())
        results_all = []
        for f in files:
            ext = f.suffix.lower()
            if ext in IMAGE_EXTS:
                r = process_image(model, str(f), save)
                if r:
                    results_all.append(r)
            elif ext in VIDEO_EXTS:
                process_video(model, str(f), save)

        # Summary for folder run
        print(f"\n{'='*55}")
        print("  Folder Run Summary")
        print(f"{'='*55}")
        for r in results_all:
            vcount = len(r["violations"])
            status = "[OK] COMPLIANT" if vcount == 0 else f"[!!] {vcount} VIOLATION(S)"
            print(f"  {Path(r['file']).name:<40} {status}")
        print(f"{'='*55}\n")

    # ── Single image ─────────────────────────
    elif src_path.suffix.lower() in IMAGE_EXTS:
        process_image(model, str(src_path), save)

    # ── Single video ─────────────────────────
    elif src_path.suffix.lower() in VIDEO_EXTS:
        process_video(model, str(src_path), save)

    else:
        print(f"[ERROR] Unsupported source: {source}")
        print(f"        Supported: {IMAGE_EXTS | VIDEO_EXTS} or a directory")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SafetyEye AI — Offline Detect")
    parser.add_argument("--source", type=str, required=True,
                        help="Path to image, video, or folder")
    parser.add_argument("--save", action="store_true",
                        help="Save annotated output to runs/detect/safetyeye_output/")
    args = parser.parse_args()
    run(args.source, args.save)