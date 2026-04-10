import streamlit as st
import cv2
import pandas as pd
import time
import os
from ultralytics import YOLO
from datetime import datetime

# ---------------- PAGE ----------------
st.set_page_config(page_title="Safety Eye Pro", layout="wide")

# ---------------- MODERN UI ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg,#020617,#0f172a);
    color: white;
}

/* Title */
.title {
    font-size: 45px;
    font-weight: bold;
    color: #38bdf8;
    text-align: center;
}

/* Glass cards */
.card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    padding: 18px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 12px;
    box-shadow: 0 0 15px rgba(0,0,0,0.3);
}

/* Alert */
.alert {
    background: rgba(255,0,0,0.2);
    border: 2px solid red;
    padding: 15px;
    border-radius: 12px;
    font-size: 22px;
    text-align: center;
    animation: blink 1s infinite;
}

@keyframes blink {
    50% { opacity: 0.5; }
}

/* Safe */
.safe {
    color: #22c55e;
    font-size: 22px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">🦺 Safety Eye Pro</p>', unsafe_allow_html=True)
st.caption("AI-Powered PPE Monitoring & Safety Intelligence System")

# ---------------- MODEL ----------------
model = YOLO("runs/detect/train9/weights/best.pt")

# ---------------- FILES ----------------
os.makedirs("screenshots", exist_ok=True)
os.makedirs("violations", exist_ok=True)

if not os.path.exists("logs.csv"):
    pd.DataFrame(columns=["Time","Type"]).to_csv("logs.csv", index=False)

# ---------------- SESSION ----------------
if "run" not in st.session_state:
    st.session_state.run = False

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙ Control Panel")
if st.sidebar.button("🚀 Start Monitoring"):
    st.session_state.run = True
if st.sidebar.button("🛑 Stop"):
    st.session_state.run = False

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["🎥 Live", "📊 Reports", "🎬 Recordings"])

# ================= LIVE =================
with tab1:
    col1, col2 = st.columns([3,1])

    frame_window = col1.image([])
    status = col1.empty()

    violation_start = None
    ALERT_TIME = 1   # 🔥 FIXED (faster logging)

    total_frames = 0
    total_violations = 0

    video_writer = None
    recording = False
    video_filename = None

    import winsound
    def beep():
        winsound.Beep(1000,300)

    if st.session_state.run:
        cap = cv2.VideoCapture(0)

        while st.session_state.run:
            ret, frame = cap.read()
            if not ret:
                st.error("Camera error")
                break

            results = model(frame)

            # ---------------- LABELS ----------------
            labels = []
            for box in results[0].boxes:
                label = model.names[int(box.cls)].lower()
                labels.append(label)

            people = sum(1 for l in labels if "person" in l)

            violation = False
            violation_type = ""

            # ---------------- PPE LOGIC ----------------
            if people > 0:
                if any("no-" in l for l in labels):
                    violation = True
                    violation_type = "PPE Missing"
                elif not any("helmet" in l or "hardhat" in l for l in labels):
                    violation = True
                    violation_type = "No Helmet"

            # ---------------- DISPLAY ----------------
            annotated = results[0].plot()
            frame_window.image(annotated, channels="BGR")

            total_frames += 1
            now = time.time()

            # ---------------- ALERT + RECORD ----------------
            if violation:
                if violation_start is None:
                    violation_start = now

                duration = now - violation_start

                if duration > ALERT_TIME:

                    total_violations += 1

                    status.markdown(
                        f'<div class="alert">🚨 {violation_type}</div>',
                        unsafe_allow_html=True
                    )

                    beep()

                    # 🎥 RECORD
                    if not recording:
                        recording = True
                        video_filename = f"violations/{int(time.time())}.avi"

                        fourcc = cv2.VideoWriter_fourcc(*'XVID')
                        h,w,_ = frame.shape
                        video_writer = cv2.VideoWriter(video_filename, fourcc, 20.0, (w,h))

                    if video_writer:
                        video_writer.write(frame)

                    # 📸 screenshot
                    cv2.imwrite(f"screenshots/{int(time.time())}.jpg", frame)

                    # 🧾 log (ALWAYS WRITE)
                    with open("logs.csv","a") as f:
                        f.write(f"{datetime.now()},{violation_type}\n")

                else:
                    status.markdown(f"⚠ {violation_type} ({duration:.1f}s)")

            else:
                violation_start = None
                status.markdown('<p class="safe">✅ SAFE ZONE</p>', unsafe_allow_html=True)

                if recording:
                    recording = False
                    if video_writer:
                        video_writer.release()
                        video_writer = None
                    st.success(f"🎬 Clip Saved!")

            # ---------------- METRICS ----------------
            safety_score = 100 - (total_violations/max(total_frames,1))*100
            st.session_state.history.append(safety_score)

            if safety_score > 90:
                risk = "LOW 🟢"
            elif safety_score > 70:
                risk = "MEDIUM 🟡"
            else:
                risk = "HIGH 🔴"

            with col2:
                st.markdown(f'<div class="card">👷 {people}<br>People</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card">⚠ {total_violations}<br>Violations</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card">🛡 {safety_score:.1f}%</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card">⚡ {risk}</div>', unsafe_allow_html=True)

            st.line_chart(st.session_state.history[-50:])

            time.sleep(0.03)

        cap.release()

# ================= REPORT =================
with tab2:
    st.subheader("📊 Safety Analytics")

    try:
        df = pd.read_csv("logs.csv")

        if not df.empty:
            st.bar_chart(df["Type"].value_counts())
            st.dataframe(df)
            st.metric("Total Violations", len(df))
        else:
            st.info("No violations yet")
    except:
        st.info("No logs")

# ================= RECORDINGS =================
with tab3:
    st.subheader("🎬 Recorded Violations")

    files = os.listdir("violations")

    if files:
        for f in files[::-1]:
            st.video(f"violations/{f}")
    else:
        st.info("No recordings yet")