import streamlit as st
import cv2
from ultralytics import YOLO
import time

st.title("📷 Webcam Monitoring")

model = YOLO("models/bestmodel.pt")

run = st.toggle("Start Webcam")

col1, col2 = st.columns([2,1])
video_box = col1.empty()
alert_box = col2.empty()

if run:
    cap = cv2.VideoCapture(1)

    while run:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640,480))
        results = model(frame, conf=0.5)

        alerts = []

        for r in results:
            for box in r.boxes:
                label = model.names[int(box.cls[0])]
                if "NO-" in label:
                    alerts.append(label.replace("NO-", "") + " Missing")

        alerts = list(set(alerts))

        annotated = results[0].plot()
        annotated = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

        video_box.image(annotated)

        # 🔥 Styled alert (like image)
        if alerts:
            alert_box.markdown(f"""
            <div style="border-radius:12px;padding:15px;
            background:rgba(255,0,0,0.1);
            border:1px solid red;
            color:white;">
            ⚠️ <b>Safety Violation</b><br>
            {'<br>'.join(alerts)}
            </div>
            """, unsafe_allow_html=True)
        else:
            alert_box.markdown("""
            <div style="border-radius:12px;padding:15px;
            background:rgba(0,255,0,0.1);
            border:1px solid green;">
            ✅ All Safe
            </div>
            """, unsafe_allow_html=True)

        time.sleep(0.03)

    cap.release()