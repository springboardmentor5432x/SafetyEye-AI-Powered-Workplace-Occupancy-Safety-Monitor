import cv2
from ultralytics import YOLO
import datetime

# Load Model
model = YOLO("models/best.pt")

# Class Names
CLASS_NAMES = {
    0: "Hardhat",
    1: "Mask",
    2: "NO-Hardhat",
    3: "NO-Mask",
    4: "NO-Safety Vest",
    5: "Person",
    6: "Safety Cone",
    7: "Safety Vest",
    8: "Machinery",
    9: "Vehicle"
}

# Violation classes
VIOLATION_CLASSES = [2, 3, 4]

# Open Webcam
cap = cv2.VideoCapture(0)
print("SafetyEye started! Press Q to quit.")

violation_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run Detection
    results = model(frame, conf=0.5)

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id   = int(box.cls[0])
            confidence = float(box.conf[0])
            label      = CLASS_NAMES.get(class_id, "Unknown")

            if class_id in VIOLATION_CLASSES:
                color = (0, 0, 255)
                violation_count += 1
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                print(f"VIOLATION DETECTED: {label} at {timestamp}")
            else:
                color = (0, 255, 0)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label} {confidence:.0%}",
                       (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       0.6, color, 2)

    # Display Info
    cv2.putText(frame, f"Violations: {violation_count}",
               (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX,
               1.0, (0, 0, 255), 2)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, timestamp,
               (10, frame.shape[0] - 10),
               cv2.FONT_HERSHEY_SIMPLEX,
               0.6, (255, 255, 255), 1)

    cv2.imshow("SafetyEye - Live Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"Session ended. Total violations detected: {violation_count}")
```
4. Commit message:
```
Add real time detection script
