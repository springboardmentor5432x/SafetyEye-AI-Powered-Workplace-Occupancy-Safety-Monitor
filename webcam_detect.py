from ultralytics import YOLO
import cv2
import os

# Load model
model = YOLO("best.pt")

# Correct save path
save_dir = r"C:\Users\klaks\Documents\safetyeye_AI\runs\detect\predict2"
os.makedirs(save_dir, exist_ok=True)

cap = cv2.VideoCapture(0)

img_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera not detected")
        break

    results = model(frame)

    annotated_frame = results[0].plot()

    cv2.imshow("SafetyEye Detection", annotated_frame)

    key = cv2.waitKey(1) & 0xFF

    # Press S to save
    if key == ord('s'):
        img_count += 1

        filename = os.path.join(save_dir, f"capture_{img_count}.jpg")

        saved = cv2.imwrite(filename, annotated_frame)

        if saved:
            print(f"\nImage saved at: {filename}")
        else:
            print("Failed to save image")

        print("Detected objects:")

        for box in results[0].boxes:
            cls_id = int(box.cls)
            conf = float(box.conf)
            name = model.names[cls_id]

            print(f"{name} → {conf:.2f}")

    # Press Q to exit
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()