import os
os.environ["STREAMLIT_WATCHDOG"] = "false"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
import cv2
import time
import csv
import tempfile
import pandas as pd
from datetime import datetime
from ultralytics import YOLO
from pathlib import Path
import winsound

# ---------------- CONFIG ----------------
VIOLATION_CLASSES = {"NO-Hardhat", "NO-Safety Vest", "NO-Mask"}
DEFAULT_IP = "http://192.168.1.5:8080/video"
LOG_FILE = "violations_log.csv"
SCREENSHOT_DIR = Path("screenshots")

# ---------------- MODEL ----------------
@st.cache_resource
def load_model():
    return YOLO("models/best.pt")

# ---------------- STATE ----------------
def init_state():
    defaults = {
        "run": False,
        "cap": None,
        "camera": "Webcam",
        "ip": DEFAULT_IP,
        "prev_logged": set(),
        "total": 0,
        "violations": 0,
        "safe": 0
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ---------------- LOGGING ----------------
def log_violation(violations):
    if not violations:
        return

    file_exists = Path(LOG_FILE).exists()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "violation"])

        for v in violations:
            writer.writerow([timestamp, v])

# ---------------- DETECTION ----------------
def detect(results, names):
    v = []
    boxes = results[0].boxes
    if boxes:
        for c in boxes.cls.tolist():
            label = names[int(c)]
            if label in VIOLATION_CLASSES:
                v.append(label)
    return v

# ---------------- DRAW ----------------
def draw(frame, results, names):
    boxes = results[0].boxes
    if boxes:
        for box in boxes:
            cls = int(box.cls[0])
            label = names[cls]
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if label in VIOLATION_CLASSES:
                color = (0, 0, 255)
            elif label in ["Hardhat", "Safety Vest"]:
                color = (0, 255, 0)
            else:
                color = (255, 255, 0)

            cv2.rectangle(frame, (x1,y1), (x2,y2), color, 2)
            cv2.putText(frame, label, (x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame

# ---------------- MAIN ----------------
def main():
    st.set_page_config(layout="wide")
    st.title("🦺 SafetyEye Dashboard")

    init_state()
    model = load_model()
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # SIDEBAR PANEL
    st.sidebar.title("Control Panel")
    sb_summary = st.sidebar.empty()
    sb_violations = st.sidebar.empty()
    sb_logs = st.sidebar.empty()
    sb_shots = st.sidebar.empty()
    sb_analytics = st.sidebar.empty()

    def render_sidebar(current_set):
        total = st.session_state.total
        vio = st.session_state.violations
        safe = st.session_state.safe
        ratio = (vio / total * 100) if total else 0

        with sb_summary.container():
            st.markdown("### Dashboard Summary")
            st.metric("Total Frames", total)
            st.metric("Total Violations", vio)
            st.metric("Safe Count", safe)
            st.metric("Detection Ratio %", f"{ratio:.2f}%")

        with sb_violations.container():
            st.markdown("### Violations Found")
            st.write("⚠ Current Violations:")
            if current_set:
                for item in sorted(current_set):
                    st.write(f"- {item}")
            else:
                st.write("- None")

        with sb_logs.container():
            st.markdown("### Logs Viewer")
            if Path(LOG_FILE).exists():
                try:
                    df = pd.read_csv(LOG_FILE)
                    st.dataframe(df.tail(10), use_container_width=True, height=180)
                except Exception:
                    st.write("Unable to read logs.")
            else:
                st.write("No logs yet.")

        with sb_shots.container():
            st.markdown("### Recent Screenshots")
            images = sorted(SCREENSHOT_DIR.glob("violation_*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
            if images:
                for img in images:
                    st.image(str(img), caption=img.name, use_container_width=True)
            else:
                st.write("No screenshots yet.")

        with sb_analytics.container():
            st.markdown("### Analytics")
            chart_df = pd.DataFrame({"Count": [safe, vio]}, index=["Safe", "Violations"])
            st.bar_chart(chart_df)

    # CONTROLS
    c1, c2, c3 = st.columns(3)

    with c1:
        st.session_state.camera = st.selectbox("Camera", ["Webcam", "IP Camera", "Upload Video"])

    with c2:
        if st.session_state.camera == "IP Camera":
            st.session_state.ip = st.text_input("Enter URL", DEFAULT_IP)
        elif st.session_state.camera == "Upload Video":
            uploaded_video = st.file_uploader("Upload Video", type=["mp4", "avi", "mov"])
        else:
            uploaded_video = None

    with c3:
        if st.button("▶ Start"):
            st.session_state.run = True
        if st.button("⏹ Stop"):
            st.session_state.run = False
            if st.session_state.cap:
                st.session_state.cap.release()
                st.session_state.cap = None

    # LAYOUT
    main_col, side_col = st.columns([2.5, 1.5])
    with main_col:
        video = st.empty()
    with side_col:
        panel_status = st.empty()
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        panel_violations = st.empty()
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        panel_analytics = st.empty()
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        panel_logs = st.empty()
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        panel_screenshots = st.empty()

    m1, m2, m3, m4 = st.columns(4)

    def render_side_panels(current_set):
        panel_style = (
            "background-color:#ffffff; border-radius:10px; padding:10px; "
            "border:1px solid #ddd; box-shadow:0 1px 6px rgba(0,0,0,0.08);"
        )

        with panel_status.container():
            st.markdown(f"<div style='{panel_style}'>", unsafe_allow_html=True)
            st.markdown("### Status Panel")
            if current_set:
                st.markdown("<h2 style='color:#dc2626;'>🔴 UNSAFE</h2>", unsafe_allow_html=True)
            else:
                st.markdown("<h2 style='color:#16a34a;'>🟢 SAFE</h2>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with panel_violations.container():
            st.markdown(f"<div style='{panel_style}'>", unsafe_allow_html=True)
            st.markdown("### Current Violations")
            if current_set:
                for v in sorted(current_set):
                    st.write(f"- {v}")
            else:
                st.write("- None")
            st.markdown("</div>", unsafe_allow_html=True)

        with panel_analytics.container():
            st.markdown(f"<div style='{panel_style}'>", unsafe_allow_html=True)
            st.markdown("### Analytics")
            total = st.session_state.total
            vio = st.session_state.violations
            safe = st.session_state.safe
            ratio = (vio / total * 100) if total else 0
            st.metric("Total Frames", total)
            st.metric("Total Violations", vio)
            st.metric("Safe Count", safe)
            st.metric("Detection Ratio %", f"{ratio:.2f}%")
            chart_df = pd.DataFrame({"Count": [safe, vio]}, index=["Safe", "Violations"])
            st.bar_chart(chart_df)
            st.markdown("</div>", unsafe_allow_html=True)

        with panel_logs.container():
            st.markdown(f"<div style='{panel_style}'>", unsafe_allow_html=True)
            st.markdown("### Logs")
            if Path(LOG_FILE).exists():
                try:
                    df = pd.read_csv(LOG_FILE)
                    st.dataframe(df.tail(10), use_container_width=True, height=170)
                except Exception:
                    st.write("Unable to read logs")
            else:
                st.write("No logs yet")
            st.markdown("</div>", unsafe_allow_html=True)

        with panel_screenshots.container():
            st.markdown(f"<div style='{panel_style}'>", unsafe_allow_html=True)
            st.markdown("### Screenshots")
            images = sorted(
                SCREENSHOT_DIR.glob("violation_*.jpg"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )[:3]
            if images:
                for img in images:
                    st.image(str(img), caption=img.name, use_container_width=True)
            else:
                st.write("No screenshots yet")
            st.markdown("</div>", unsafe_allow_html=True)

    # LOOP
    if st.session_state.run:

        # OPEN CAMERA ONCE
        if st.session_state.cap is None:
            if st.session_state.camera == "Webcam":
                src = 0
            elif st.session_state.camera == "IP Camera":
                src = st.session_state.ip
            else:
                if uploaded_video is None:
                    video.info("Upload a video file to start")
                    st.session_state.run = False
                    return

                suffix = Path(uploaded_video.name).suffix or ".mp4"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uploaded_video.getbuffer())
                    src = tmp.name

            st.session_state.cap = cv2.VideoCapture(src)

        cap = st.session_state.cap

        while st.session_state.run:
            ret, frame = cap.read()

            if not ret:
                if st.session_state.camera == "Upload Video":
                    st.info("Video ended")
                else:
                    st.error("Camera not working")
                break

            results = model(frame, verbose=False)
            violations = detect(results, model.names)
            frame = draw(frame, results, model.names)

            # ---------------- FIX: NO DUPLICATE LOGGING ----------------
            current_set = set(violations)
            prev_set = st.session_state.prev_logged

            new_violations = current_set - prev_set

            if new_violations:
                log_violation(new_violations)
                st.session_state.violations += len(new_violations)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                shot_path = SCREENSHOT_DIR / f"violation_{ts}.jpg"
                cv2.imwrite(str(shot_path), frame)
                try:
                    winsound.Beep(1000, 1000)
                except Exception:
                    pass

            st.session_state.prev_logged = current_set

            # SAFE COUNT
            if not violations:
                st.session_state.safe += 1

            st.session_state.total += 1

            # DISPLAY
            video.image(frame, channels="BGR")

            render_side_panels(current_set)

            # METRICS
            total = st.session_state.total
            vio = st.session_state.violations
            safe = st.session_state.safe
            ratio = (vio/total*100) if total else 0

            m1.metric("Frames", total)
            m2.metric("Violations", vio)
            m3.metric("Safe", safe)
            m4.metric("Ratio", f"{ratio:.2f}%")

            render_sidebar(current_set)

            time.sleep(0.03)

    else:
        video.info("Click Start Monitoring")
        render_side_panels(set())
        render_sidebar(set())

if __name__ == "__main__":
    main()