from ultralytics import YOLO
import cv2

# Load your trained model
model = YOLO("models/best.pt")

# Open webcam
cap = cv2.VideoCapture(1)

print("Press 'q' to exit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO detection
    results = model(frame, conf=0.6, iou=0.5)

    # Draw detections
    annotated_frame = results[0].plot()

    # Show result
    cv2.imshow("SafetyEye Real-Time Detection", annotated_frame)

    # Exit key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()