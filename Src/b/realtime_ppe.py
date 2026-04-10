import cv2
import time
from ultralytics import YOLO


model = YOLO("runs/detect/train9/weights/best.pt")

cap = cv2.VideoCapture(0)


prev_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame = cv2.resize(frame, (640, 480))

    
    results = model(frame, conf=0.25, imgsz=640)


    annotated_frame = results[0].plot()

    detections = results[0].boxes

    persons = []
    helmets = []
    vests = []

    # 🔹 Class-wise detection separation
    for box in detections:
        cls = int(box.cls[0])
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        label = model.names[cls]

        if label == "Person":
            persons.append((x1, y1, x2, y2))
        elif label == "Hardhat":
            helmets.append((x1, y1, x2, y2))
        elif label == "Vest":
            vests.append((x1, y1, x2, y2))

    # 🔹 VIOLATION LOGIC
    for (px1, py1, px2, py2) in persons:

        has_helmet = False
        has_vest = False

        # Check helmet inside person box
        for (hx1, hy1, hx2, hy2) in helmets:
            if hx1 > px1 and hx2 < px2 and hy1 > py1 and hy2 < py2:
                has_helmet = True

        # Check vest inside person box
        for (vx1, vy1, vx2, vy2) in vests:
            if vx1 > px1 and vx2 < px2 and vy1 > py1 and vy2 < py2:
                has_vest = True

        # 🚨 ALERTS
        if not has_helmet:
            cv2.putText(annotated_frame, "NO HELMET!", (px1, py1 - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            print("⚠️ Helmet violation detected")

        if not has_vest:
            cv2.putText(annotated_frame, "NO VEST!", (px1, py1 - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            print("⚠️ Vest violation detected")

    # 🔹 Add system title
    cv2.putText(annotated_frame, "SAFETY MONITORING SYSTEM", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    # 🔹 FPS Calculation
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
    prev_time = curr_time

    cv2.putText(annotated_frame, f"FPS: {int(fps)}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # 🔹 Show output
    cv2.imshow("PPE Detection System", annotated_frame)

    # Press ESC to exit
    if cv2.waitKey(1) & 0xFF == 27:
        break

# 🔹 Release resources
cap.release()
cv2.destroyAllWindows()