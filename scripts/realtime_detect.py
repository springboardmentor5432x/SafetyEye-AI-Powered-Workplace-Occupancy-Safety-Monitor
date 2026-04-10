import cv2
from ultralytics import YOLO
import time
import os
import logging

# 🔕 Disable YOLO logs
logging.getLogger("ultralytics").setLevel(logging.ERROR)

# Load model
model = YOLO("models/best.pt")

# Open webcam
cap = cv2.VideoCapture(0)

last_alert = ""

# Function for clean CMD alert display
def show_alert(alert_text):
    os.system('cls')  # Clear CMD (Windows)

    print("===================================")
    print("        ⚠ SAFETY ALERT SYSTEM ⚠")
    print("===================================\n")

    print(f"TIME: {time.strftime('%H:%M:%S')}\n")

    if alert_text:
        print("🚨 STATUS: VIOLATION DETECTED 🚨\n")
        print(f"⚠ ALERT: {alert_text}\n")
    else:
        print("✅ STATUS: ALL SAFE\n")

    print("===================================")


while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 🔥 Run detection WITHOUT logs
    results = model(frame, verbose=False)

    annotated_frame = results[0].plot()

    boxes = results[0].boxes
    names = model.names

    persons = []
    helmets = []
    vests = []

    # Collect objects
    for box in boxes:
        cls_id = int(box.cls[0])
        label = names[cls_id]

        if label == "Person":
            persons.append(box)
        elif label == "Hardhat":
            helmets.append(box)
        elif label == "Safety Vest":
            vests.append(box)

    current_alert = ""

    # Check violations
    for person in persons:
        px1, py1, px2, py2 = map(int, person.xyxy[0])

        helmet_found = False
        vest_found = False

        # Check helmet
        for helmet in helmets:
            hx1, hy1, hx2, hy2 = map(int, helmet.xyxy[0])
            if abs(px1 - hx1) < 100 and abs(py1 - hy1) < 100:
                helmet_found = True

        # Check vest
        for vest in vests:
            vx1, vy1, vx2, vy2 = map(int, vest.xyxy[0])
            if abs(px1 - vx1) < 100 and abs(py1 - vy1) < 100:
                vest_found = True

        # Build alert message
        alert_text = ""

        if not helmet_found:
            alert_text += "NO HELMET "

        if not vest_found:
            alert_text += "NO VEST"

        # Show alert on video
        if alert_text:
            cv2.putText(annotated_frame, alert_text, (px1, py1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

            current_alert = alert_text

    # Update CMD only when alert changes
    if current_alert != last_alert:
        show_alert(current_alert)
        last_alert = current_alert

    # Show video
    cv2.imshow("SafetyEye Monitoring", annotated_frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()