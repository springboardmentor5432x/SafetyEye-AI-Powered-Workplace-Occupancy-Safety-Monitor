import cv2
import time
import argparse
from datetime import datetime
from ultralytics import YOLO
 
#  SETTINGS  —  change these values to customise the system
 
# Path to the YOLOv8 model trained in Milestone 2
MODEL_PATH = "/Users/utkarstdawar/Desktop/SafetyEye/runs/detect/train7/weights/best.pt"
 
# Only accept detections with this confidence score or higher (0.0 – 1.0)
# Lower = more detections but more false positives
# Higher = fewer detections but more accurate
CONFIDENCE_THRESHOLD = 0.5
 
# Process every Nth frame to keep the video smooth
# 1 = process every frame (slower), 2 = every 2nd frame (faster)
FRAME_SKIP = 2
 
# Seconds to wait before repeating the same alert
# Prevents the console from being spammed every frame
ALERT_COOLDOWN_SECONDS = 10
 
# Safety rules: what counts as a violation
# Format: "violation message" -> [list of YOLO class names that satisfy the rule]
# If ANY class in the list is found near a person, the rule is satisfied (no violation)
PPE_RULES = {
    "No helmet worn":     ["hardhat"],
    "No safety vest worn": ["vest"],
}
 
# How much two bounding boxes must overlap before we say
# a PPE item "belongs to" a nearby person (0.0 = no overlap needed, 1.0 = identical boxes)
# 0.05 means just 5% overlap is enough — keeps detection sensitive
OVERLAP_THRESHOLD = 0.05
 
# Bounding box colors in BGR format (Blue, Green, Red — OpenCV uses BGR not RGB)
COLOR_PPE_SAFE  = (0,   210, 0)    # Green  — worker is wearing the PPE item
COLOR_PERSON    = (180, 180, 180)  # Gray   — person detected
COLOR_OTHER     = (0,   200, 255)  # Yellow — other objects (machinery, vehicles)
COLOR_VIOLATION = (0,   0,   220)  # Red    — violation warning banner
 
 
#  PART 1 — VIDEO LOOP
#  Opens the camera and runs the pipeline on every frame

 
def run(source, model_path=MODEL_PATH):
    """
    Main function. Opens the video source and runs an infinite loop where
    each iteration processes one frame through the full detection pipeline.
 
    The pipeline per frame is:
        read frame -> detect objects -> check violations -> draw overlays -> alert -> display
    """
 
    # Load the model ONCE here, before the loop starts.
    # Loading takes 1-2 seconds — if we did it inside the loop,
    # the video would freeze on every single frame.
    print(f"\n[SafetyEye] Loading model from: {model_path}")
    model = YOLO(model_path)
    print("[SafetyEye] Model loaded successfully.")
    print("[SafetyEye] Starting live detection — press Q to quit.\n")
 
    # Open the video source:
    #   cv2.VideoCapture(0)         -> opens the default webcam (index 0)
    #   cv2.VideoCapture("x.mp4")  -> opens a video file from disk
    cap = cv2.VideoCapture(source)
 
    if not cap.isOpened():
        print(f"[ERROR] Could not open video source: {source}")
        print("        Check that your webcam is connected, or the file path is correct.")
        return
 
    # Tracking variables used across frames
    frame_count  = 0
    last_alerted = {}    # remembers when each violation type was last alerted
    fps_tracker  = {"count": 0, "start": time.time(), "value": 0.0}
 
    # Main loop — runs until the video ends or the user presses Q
    while True:
 
        # Read one frame from the video source
        # ret   -> True if the frame was read successfully
        # frame -> the image as a NumPy array of shape (height, width, 3)
        ret, frame = cap.read()
 
        if not ret:
            # Happens when a video file finishes, or webcam disconnects
            print("[SafetyEye] Video stream ended or could not read frame.")
            break
 
        frame_count += 1
 
        # Skip frames to improve performance on slower computers.
        # e.g. if FRAME_SKIP=2, we only process frames 2, 4, 6, 8 ...
        if frame_count % FRAME_SKIP != 0:
            continue
 
        # STEP 1: Detect objects in this frame using YOLOv8
        detections = detect_objects(model, frame)
 
        # STEP 2: Check which persons are missing required PPE
        violations = find_violations(detections)
 
        # STEP 3: Draw bounding boxes and warning banners on the frame
        annotated_frame = draw_results(frame, detections, violations)
 
        # STEP 4: Print console alerts for any new violations
        send_alerts(violations, last_alerted)
 
        # STEP 5: Show FPS counter in the top-left corner of the frame
        fps = calculate_fps(fps_tracker)
        cv2.putText(annotated_frame, f"FPS: {fps:.1f}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
 
        # STEP 6: Display the annotated frame in a window
        cv2.imshow("SafetyEye — Live Monitor", annotated_frame)
 
        # Wait 1ms and check if the user pressed Q to quit.
        # cv2.waitKey() is required for OpenCV to actually render the window.
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("[SafetyEye] Quit by user.")
            break
 
    # Cleanup: always release the camera and close all windows
    cap.release()
    cv2.destroyAllWindows()
    print("[SafetyEye] Stopped cleanly.")
 
 
#  PART 2 — YOLOV8 OBJECT DETECTION
#  Runs the trained model on one frame and returns what was found
 
def detect_objects(model, frame) -> list[dict]:
    """
    Passes one video frame through the YOLOv8 model and returns
    a list of everything the model detected.
 
    Each detection is returned as a simple dictionary:
        {
            "class":      "hardhat",         <- what was detected
            "confidence": 0.91,              <- how confident (0 to 1)
            "box":        (x1, y1, x2, y2)  <- bounding box pixel coordinates
        }
 
    Box coordinates:
        (x1, y1) = top-left corner
        (x2, y2) = bottom-right corner
    """
 
    # Run inference — verbose=False stops Ultralytics printing to console every frame
    results = model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
 
    # results is a list with one entry per image passed in.
    # Since we pass one frame at a time, we always use results[0].
    result = results[0]
 
    detections = []
 
    for box in result.boxes:
        # box.cls  -> numeric class ID (e.g. 0, 1, 2 ...)
        # box.conf -> confidence score between 0 and 1
        # box.xyxy -> bounding box as [[x1, y1, x2, y2]]
 
        class_id   = int(box.cls[0])
        class_name = result.names[class_id]   # convert ID to readable name like "hardhat"
        confidence = float(box.conf[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])
 
        detections.append({
            "class":      class_name,
            "confidence": confidence,
            "box":        (x1, y1, x2, y2)
        })
 
    return detections
 
 

#  PART 3 — VIOLATION RULE ENGINE
#  Checks every detected person to see if they have required PPE
 
def find_violations(detections: list[dict]) -> list[dict]:
    """
    Loops through every detected person and checks whether their
    required PPE (helmet, vest, etc.) is also visible nearby.
 
    Returns a list of violations found, each as a dictionary:
        {
            "type":       "No helmet worn",   <- which rule was broken
            "person_id":  1,                  <- which person (1, 2, 3 ...)
            "person_box": (x1, y1, x2, y2)   <- where that person is in the frame
        }
    """
 
    # Separate persons from PPE items in the full detections list
    persons   = [d for d in detections if d["class"] == "person"]
    ppe_items = [d for d in detections if d["class"] != "person"]
 
    violations = []
 
    for index, person in enumerate(persons):
 
        # Find all PPE class names that are spatially close to this person
        nearby_ppe = get_nearby_ppe_classes(person["box"], ppe_items)
 
        # Check each safety rule defined in PPE_RULES
        for violation_name, required_classes in PPE_RULES.items():
 
            # Rule is satisfied if ANY of the required classes are near this person
            rule_satisfied = any(cls in nearby_ppe for cls in required_classes)
 
            if not rule_satisfied:
                violations.append({
                    "type":       violation_name,
                    "person_id":  index + 1,       # count from 1, not 0
                    "person_box": person["box"]
                })
 
    return violations
 
 
def get_nearby_ppe_classes(person_box: tuple, ppe_items: list[dict]) -> set[str]:
    """
    Returns the set of PPE class names that are spatially close to the given person.
 
    Two checks are used to decide if a PPE item belongs to a person:
 
    Check 1 — Bounding box overlap (IoU):
        Measures how much the person box and PPE box overlap each other.
        A helmet on top of a person's head will overlap with their bounding box.
 
    Check 2 — Centre point inside person box:
        Checks if the centre of the PPE box falls inside the person box.
        This catches helmets sitting just above the head — their box may
        barely overlap, but their centre point will be near the person's head.
    """
    nearby_classes = set()
 
    for ppe in ppe_items:
        overlap          = calculate_iou(person_box, ppe["box"])
        centre_is_inside = is_centre_inside(ppe["box"], person_box)
 
        if overlap > OVERLAP_THRESHOLD or centre_is_inside:
            nearby_classes.add(ppe["class"])
 
    return nearby_classes
 
 
def calculate_iou(box_a: tuple, box_b: tuple) -> float:
    """
    Calculates IoU (Intersection over Union) between two bounding boxes.
 
    IoU measures how much two boxes overlap:
        0.0 = boxes do not touch at all
        1.0 = boxes are identical
 
    Diagram:
        ┌────────────────┐
        │    Box A       │
        │       ┌────────┼──────┐
        │       │ SHARED │      │
        └───────┼────────┘      │
                │    Box B      │
                └───────────────┘
 
        IoU = area of SHARED region / total area covered by BOTH boxes
    """
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
 
    # Find the coordinates of the region where both boxes overlap
    overlap_x1 = max(ax1, bx1)
    overlap_y1 = max(ay1, by1)
    overlap_x2 = min(ax2, bx2)
    overlap_y2 = min(ay2, by2)
 
    # max(0, ...) gives 0 if there is no overlap (would otherwise be negative)
    overlap_width  = max(0, overlap_x2 - overlap_x1)
    overlap_height = max(0, overlap_y2 - overlap_y1)
    overlap_area   = overlap_width * overlap_height
 
    # If there is no overlap at all, return 0 straight away
    if overlap_area == 0:
        return 0.0
 
    # Calculate the total area covered by both boxes combined
    area_a     = (ax2 - ax1) * (ay2 - ay1)
    area_b     = (bx2 - bx1) * (by2 - by1)
    union_area = area_a + area_b - overlap_area  # subtract overlap so it's not counted twice
 
    return overlap_area / union_area if union_area > 0 else 0.0
 
 
def is_centre_inside(inner_box: tuple, outer_box: tuple) -> bool:
    """
    Returns True if the centre point of inner_box falls inside outer_box.
 
    Why this is needed:
        A worker's helmet sits above their head. The helmet bounding box
        may not overlap much with the person bounding box, but the centre
        of the helmet box will still land near the top of the person box.
        This check catches those edge cases that IoU alone would miss.
    """
    ix1, iy1, ix2, iy2 = inner_box
    ox1, oy1, ox2, oy2 = outer_box
 
    # Calculate the centre point of the inner box
    centre_x = (ix1 + ix2) / 2
    centre_y = (iy1 + iy2) / 2
 
    # Return True if the centre point falls within the outer box boundaries
    return ox1 <= centre_x <= ox2 and oy1 <= centre_y <= oy2
 
 
#  PART 4 — DRAWING OVERLAYS
#  Draws bounding boxes and violation banners onto the video frame
 
def draw_results(frame, detections: list[dict], violations: list[dict]):
    """
    Draws two things onto a copy of the frame:
 
    1. A colored bounding box around every detected object:
           Green  -> PPE item (helmet, vest, mask) — safe
           Gray   -> person
           Yellow -> other objects (machinery, vehicle)
 
    2. A red warning banner at the top of the screen for each violation
 
    Returns the annotated frame. The original frame is NOT changed.
    """
 
    # Always work on a copy — never draw directly on the original frame
    output_frame = frame.copy()
 
    # Draw a bounding box for each detected object
    for det in detections:
        x1, y1, x2, y2 = det["box"]
        label          = det["class"]
        confidence     = det["confidence"]
 
        # Pick the box color based on what was detected
        if label in ("hardhat", "vest", "mask"):
            color = COLOR_PPE_SAFE   # green — safety equipment present
        elif label == "person":
            color = COLOR_PERSON     # gray — person
        else:
            color = COLOR_OTHER      # yellow — machinery, vehicles, etc.
 
        # Draw the rectangle border around the detected object
        cv2.rectangle(output_frame, (x1, y1), (x2, y2), color, thickness=2)
 
        # Build the label text shown above the box, e.g. "hardhat 91%"
        label_text = f"{label} {confidence:.0%}"
 
        # Measure how wide the text will be so we can size the background behind it
        (text_width, text_height), _ = cv2.getTextSize(
            label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1
        )
 
        # Draw a filled colored background pill above the box for readability
        cv2.rectangle(
            output_frame,
            (x1, y1 - text_height - 8),   # top-left of background
            (x1 + text_width + 4, y1),     # bottom-right of background
            color,
            thickness=-1                   # -1 = filled rectangle
        )
 
        # Draw the label text in black on the colored background
        cv2.putText(output_frame, label_text,
                    (x1 + 2, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), thickness=1)
 
    # Draw a red violation banner for each violation found
    # Banners are stacked vertically starting just below the FPS counter
    for i, violation in enumerate(violations):
        banner_y = 70 + (i * 35)   # each banner is 35px below the previous one
 
        # Draw the red filled banner rectangle across the full width of the frame
        cv2.rectangle(
            output_frame,
            (0, banner_y - 25),
            (frame.shape[1], banner_y + 5),  # frame.shape[1] = frame width in pixels
            COLOR_VIOLATION,
            thickness=-1
        )
 
        # Draw the white violation text on the banner
        banner_text = f"  VIOLATION: {violation['type']}  (Person #{violation['person_id']})"
        cv2.putText(output_frame, banner_text,
                    (10, banner_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), thickness=2)
 
    return output_frame
 
 
#  PART 5 — ALERT SYSTEM
#  Notifies supervisors when violations are detected

 
def send_alerts(violations: list[dict], last_alerted: dict):
    """
    Prints a formatted alert to the console for each new violation,
    and saves every alert to violation_log.txt for record-keeping.
 
    WHY THROTTLING IS NEEDED:
        The detection loop runs ~15-30 times per second. Without throttling,
        the same "No helmet" alert would print hundreds of times per minute.
        The last_alerted dictionary tracks the last time each violation type
        was alerted, and skips re-alerting until ALERT_COOLDOWN_SECONDS pass.
 
    Parameters:
        violations   -> list of violation dicts from find_violations()
        last_alerted -> shared dict that tracks alert timing across frames
                        e.g. {"No helmet worn": 1715000000.0}
    """
    current_time = time.time()
 
    for violation in violations:
        v_type = violation["type"]
 
        # Check how long ago this violation type was last alerted
        time_since_last = current_time - last_alerted.get(v_type, 0)
 
        if time_since_last < ALERT_COOLDOWN_SECONDS:
            continue   # not enough time has passed — skip
 
        # Record that we are alerting this type right now
        last_alerted[v_type] = current_time
 
        timestamp = datetime.now().strftime("%H:%M:%S")
 
        # Print a formatted alert to the console
        print(f"+-----------------------------------------+")
        print(f"|  !! SAFETY VIOLATION DETECTED           |")
        print(f"|  Time   : {timestamp}                   |")
        print(f"|  Type   : {v_type:<30} |")
        print(f"|  Person : #{violation['person_id']}                           |")
        print(f"+-----------------------------------------+\n")
 
        # Append the violation to the log file (creates the file if it doesn't exist)
        log_entry = (
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  "
            f"VIOLATION | {v_type} | Person #{violation['person_id']}\n"
        )
        with open("violation_log.txt", "a") as log_file:
            log_file.write(log_entry)
 
 
#  PART 6 — FPS COUNTER
#  Shows how many frames per second the system is processing
 
def calculate_fps(tracker: dict) -> float:
    """
    Calculates a rolling frames-per-second reading.
 
    The tracker dictionary holds state between calls:
        "count" -> frames processed in the current 1-second window
        "start" -> when the current window began
        "value" -> the most recent FPS reading to display
 
    FPS is recalculated once per second to avoid the number flickering.
    """
    tracker["count"] += 1
    elapsed = time.time() - tracker["start"]
 
    if elapsed >= 1.0:
        # One full second has passed — calculate and store the new FPS
        tracker["value"] = tracker["count"] / elapsed
        tracker["count"] = 0
        tracker["start"] = time.time()
 
    return tracker["value"]
 
 
#  ENTRY POINT

if __name__ == "__main__":
 
    parser = argparse.ArgumentParser(
        description="SafetyEye – Real-Time PPE Detection (Milestone 3)"
    )
    parser.add_argument(
        "--source",
        type=str,
        default="0",
        help="Video source: '0' for webcam, or path to a .mp4 video file"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=MODEL_PATH,
        help="Path to your trained YOLOv8 .pt model file"
    )
    args = parser.parse_args()
 
    # Convert "0" string to integer for OpenCV webcam index.
    # OpenCV needs an int for webcam (e.g. 0), but a string for file paths.
    source = int(args.source) if args.source.isdigit() else args.source
 
    run(source, args.model)