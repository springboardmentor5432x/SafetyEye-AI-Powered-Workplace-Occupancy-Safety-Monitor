import streamlit as st
import cv2
from ultralytics import YOLO
import os
import time

st.title("🎥 Dataset Video Monitoring")

model = YOLO("models/bestmodel.pt")

video_folder = "dataset/videos"
videos = os.listdir(video_folder)

selected_video = st.selectbox("Select Video", videos)

run = st.toggle("Start Video")

col1, col2 = st.columns([2,1])
video_box = col1.empty()
alert_box = col2.empty()

if run:
    cap = cv2.VideoCapture(os.path.join(video_folder, selected_video))

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

        if alerts:
            alert_box.error("⚠️ " + ", ".join(alerts))
        else:
            alert_box.success("✅ All Safe")

        time.sleep(0.03)

    cap.release()