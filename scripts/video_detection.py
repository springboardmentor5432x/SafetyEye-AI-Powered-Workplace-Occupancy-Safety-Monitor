from ultralytics import YOLO
import cv2

# Load model
model = YOLO("models/bestmodel.pt")

# Load video
cap = cv2.VideoCapture("dataset/videos/fullsaftey.mp4")

if not cap.isOpened():
    print("Error: Cannot open video")
    exit()

print("Video Detection Started... Press Q to exit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize (optional for smooth performance)
    frame = cv2.resize(frame, (640, 480))

    # YOLO detection
    results = model(frame, conf=0.5)

    # Draw YOLO boxes
    annotated_frame = results[0].plot()

    alerts = []

    for r in results:
        boxes = r.boxes

        persons = []
        others = []

        for box in boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            xyxy = box.xyxy[0].tolist()

            if label == "Person":
                persons.append(xyxy)
            else:
                others.append((label, xyxy))

        # Check each person
        for px1, py1, px2, py2 in persons:

            has_helmet = False
            has_vest = False
            has_mask = False

            for label, (ox1, oy1, ox2, oy2) in others:

                # Check if object inside person box
                if ox1 > px1 and oy1 > py1 and ox2 < px2 and oy2 < py2:

                    if label == "Hardhat":
                        has_helmet = True
                    if label == "Safety Vest":
                        has_vest = True
                    if label == "Mask":
                        has_mask = True

            unsafe = False

            if not has_helmet:
                alerts.append("Helmet Missing")
                unsafe = True

            if not has_vest:
                alerts.append("Safety Vest Missing")
                unsafe = True

            if not has_mask:
                alerts.append("Mask Missing")
                unsafe = True

            # 🔴 DRAW RED BOX FOR UNSAFE PERSON
            if unsafe:
                cv2.rectangle(
                    annotated_frame,
                    (int(px1), int(py1)),
                    (int(px2), int(py2)),
                    (0, 0, 255),  # Red color
                    3
                )

    # Remove duplicates
    alerts = list(set(alerts))

    # Display alerts
    y = 40
    for alert in alerts:
        cv2.putText(
            annotated_frame,
            "ALERT: " + alert,
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
            cv2.LINE_AA
        )
        y += 30

    # Show video
    cv2.imshow("SafetyEye - Video Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()