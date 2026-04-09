import cv2
import time
import sys
from ultralytics import YOLO
from scripts.violation_rules import ViolationRuleEngine
from scripts.alert_system import AlertSystem

#  colors for different classes
CLASS_COLORS = {
    "Hardhat":         (0, 255, 0),      # Green
    "Safety Vest":     (0, 200, 100),    # Teal-green
    "Mask":            (0, 180, 255),    # Cyan
    "Person":          (255, 200, 0),    # Yellow
    "NO-Hardhat":      (0, 0, 255),      # Red
    "NO-Safety Vest":  (0, 0, 200),      # Dark red
    "NO-Mask":         (100, 0, 200),    # Purple-red
    "Machinery":       (180, 180, 180),  # Gray
    "Vehicle":         (150, 100, 200),  # Purple
}
DEFAULT_COLOR = (200, 200, 200)

def main():
    model_path = "/Users/utkarstdawar/Desktop/SafetyEye/models/best.pt"
    
    # --- CHOOSE VIDEO SOURCE ---
    video_source = 0
   # video_source = "/Users/utkarstdawar/Desktop/SafetyEye/milestone3/indianworkers.mp4"

    print("Loading YOLO model...")
    model = YOLO(model_path)
    print("Model loaded successfully.")

    rules = ViolationRuleEngine()
    alerts = AlertSystem()

    last_alert_time = {}
    cooldown_seconds = 5

    active_display_violations = {}
    visual_persist_time = 1.5 

    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    print("Starting video feed. Press 'q' to quit.")

    frame_count = 0
    start_time = time.time()

    last_detected_items = []
    last_persons_count = 0
    fps = 0

    # Ensure current_violations exists outside the if block
    current_violations = []

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Video stream ended.")
            break

        frame_count += 1
        elapsed = time.time() - start_time
        if frame_count % 30 == 0:  
            fps = frame_count / elapsed if elapsed > 0 else 0

        now = time.time()

        # 1. DETECTION PHASE 
        if frame_count % 2 == 0:
            results = model.predict(frame, conf=0.40, verbose=False)[0]

            last_detected_items = []
            last_persons_count = 0

            for box_data in results.boxes:
                class_id = int(box_data.cls[0])
                label = model.names[class_id]
                conf = float(box_data.conf[0])
                
                x1, y1, x2, y2 = map(int, box_data.xyxy[0].cpu().numpy())

                last_detected_items.append({"label": label, "box": [x1, y1, x2, y2], "conf": conf})

                if label == "Person":
                    last_persons_count += 1

            # Check rules using the newest detections
            current_violations = rules.check_violations(last_detected_items)
            
            # Keep track of when we last saw this violation for the screen banner
            for v in current_violations:
                active_display_violations[v] = now

        # 2. DRAWING PHASE (Runs EVERY frame) 
        
        # Draw bounding boxes from the last known detections
        for item in last_detected_items:
            label = item["label"]
            conf = item["conf"]
            x1, y1, x2, y2 = item["box"]

            color = CLASS_COLORS.get(label, DEFAULT_COLOR)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            text = f"{label} {conf:.2f}"
            (tw, th), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            text_color = (0, 0, 0) if sum(color) > 400 else (255, 255, 255)
            
            cv2.rectangle(frame, (x1, y1 - th - baseline - 5), (x1 + tw, y1), color, -1)
            cv2.putText(frame, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)

        # Draw the dark stats background
        cv2.rectangle(frame, (0, 0), (280, 80), (30, 30, 30), -1)
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, f"People: {last_persons_count}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Update which violations should still be shown on screen
        violations_to_display = []
        for v, last_seen in list(active_display_violations.items()):
            if (now - last_seen) < visual_persist_time:
                violations_to_display.append(v)
            else:
                del active_display_violations[v]

        # Draw the Red Warning Banner
        if len(violations_to_display) > 0:
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (frame.shape[1], 40), (0, 0, 200), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            summary = " | ".join(set(violations_to_display))[:80]
            cv2.putText(frame, f"VIOLATION: {summary}", (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        # --- 3. ALERT TRIGGER PHASE (Screenshots will now have ALL drawings) ---
        if frame_count % 2 == 0:
            for v in current_violations:
                if v not in last_alert_time or (now - last_alert_time[v]) > cooldown_seconds:
                    alerts.trigger_alert(v, frame)  # Ab yeh puri tarah se draw kiya hua frame bheja jayega
                    last_alert_time[v] = now

        # Show the final completely annotated frame
        cv2.imshow("SafetyEye - Live Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    print("\n--- Session Summary ---")
    print("Total violations recorded:", alerts.total_violations)
    for msg, count in alerts.violation_counts.items():
        print(f" - {msg}: {count} times")

if __name__ == "__main__":
    main()