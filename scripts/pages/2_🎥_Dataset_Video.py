import streamlit as st
import cv2
from ultralytics import YOLO
import os
import time
import sys
import os

# Ensure we can import from scripts/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from audio_utils import play_alarm

st.set_page_config(page_title="Video Testing – SafetyEye", page_icon="📂", layout="wide")

# Shared premium CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; background-color: #0a0e1a !important; color: #e2e8f0 !important; }
    .stApp { background: radial-gradient(ellipse at top right, #0f1628, #0a0e1a, #060912) !important; }
    #MainMenu, footer, header { visibility: hidden !important; }
    .page-header { padding: 10px 0 20px 0; border-bottom: 1px solid rgba(77,166,255,0.1); margin-bottom: 24px; }
    .page-title  { font-size: 1.5rem; font-weight: 800; background: linear-gradient(135deg, #e2e8f0, #4da6ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .page-sub    { font-size: 0.82rem; color: #4a5568; margin-top: 4px; }
    .video-wrapper { background: rgba(10,14,26,0.9); border: 1.5px solid rgba(0,255,136,0.35); border-radius: 18px; overflow: hidden; box-shadow: 0 0 24px rgba(0,255,136,0.12); padding: 4px; }
    .alert-panel { background: rgba(10,14,26,0.6); border: 1px solid rgba(77,166,255,0.1); border-radius: 16px; padding: 14px; }
    .alert-card-unsafe { display:flex; align-items:flex-start; gap:10px; background:rgba(255,68,68,0.07); border:1px solid rgba(255,68,68,0.3); border-left:3px solid #ff4444; border-radius:10px; padding:10px 12px; margin-bottom:8px; box-shadow:0 0 10px rgba(255,68,68,0.08); }
    .alert-card-safe   { display:flex; align-items:center; gap:10px; background:rgba(0,255,136,0.07); border:1px solid rgba(0,255,136,0.3); border-left:3px solid #00ff88; border-radius:10px; padding:10px 12px; margin-bottom:8px; box-shadow:0 0 10px rgba(0,255,136,0.08); }
    .alert-title { font-size:0.82rem; font-weight:700; color:#e2e8f0; margin-bottom:2px; }
    .alert-meta  { font-size:0.72rem; color:#4a5568; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg,#0d1117,#0a0e1a,#060912) !important; border-right: 1px solid rgba(77,166,255,0.15) !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="page-header">
        <div class="page-title">📂 Video Testing</div>
        <div class="page-sub">Dataset video PPE detection analysis</div>
    </div>
""", unsafe_allow_html=True)

model = YOLO("models/bestmodel.pt")

video_folder = "dataset/videos"
videos = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi'))] if os.path.exists(video_folder) else []

col_ctrl, _ = st.columns([1, 3])
with col_ctrl:
    selected_video = st.selectbox("📁 Select Video", videos) if videos else None
    if not videos:
        st.warning("No videos in dataset/videos/")
    run = st.toggle("▶  Start Video", key="vid_run")
    
    # Alarm state initialization and toggle
    if 'alarm_enabled' not in st.session_state:
        st.session_state.alarm_enabled = True
    if 'last_alarm_time' not in st.session_state:
        st.session_state.last_alarm_time = 0.0
        
    st.session_state.alarm_enabled = st.toggle("🔔 Enable Alarm", value=st.session_state.alarm_enabled, key="video_alarm_toggle")

col1, col2 = st.columns([2, 1], gap="medium")

with col1:
    st.markdown('<div class="video-wrapper">', unsafe_allow_html=True)
    video_box = st.empty()
    video_box.image(
        __import__('numpy').zeros((360, 480, 3), dtype=__import__('numpy').uint8),
        channels="RGB", use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("**Live Alerts & Violations**")
    alert_box = st.empty()
    alert_box.markdown('<div class="alert-panel"><div class="alert-card-safe"><span>✅</span><div><div class="alert-title">All Safe</div><div class="alert-meta">Waiting for feed…</div></div></div></div>', unsafe_allow_html=True)

if run and selected_video:
    import datetime
    cap = cv2.VideoCapture(os.path.join(video_folder, selected_video))

    while run:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame = cv2.resize(frame, (640, 480))
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
        video_box.image(annotated, use_container_width=True)

        ts = datetime.datetime.now().strftime("%H:%M:%S")
        if alerts:
            cards = "".join([f'<div class="alert-card-unsafe"><span>⚠️</span><div><div class="alert-title">{a}</div><div class="alert-meta">{ts}</div></div></div>' for a in alerts])
            alert_box.markdown(f'<div class="alert-panel">{cards}</div>', unsafe_allow_html=True)
        else:
            alert_box.markdown(f'<div class="alert-panel"><div class="alert-card-safe"><span>✅</span><div><div class="alert-title">All Safe</div><div class="alert-meta">{ts}</div></div></div></div>', unsafe_allow_html=True)

        # ── Alarm Logic ──────────────────────────────────
        if alerts and st.session_state.alarm_enabled:
            current_time = time.time()
            if current_time - st.session_state.last_alarm_time > 4.0:
                play_alarm()
                st.session_state.last_alarm_time = current_time

        time.sleep(0.03)

    cap.release()