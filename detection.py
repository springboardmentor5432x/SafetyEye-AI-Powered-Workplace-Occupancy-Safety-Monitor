from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")  # working model

cap = cv2.VideoCapture(0)

print("Starting camera...")

while True:
    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame)

    annotated_frame = results[0].plot()

    cv2.imshow("Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == 27:  # press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()