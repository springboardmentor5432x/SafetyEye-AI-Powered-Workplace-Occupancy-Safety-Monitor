import streamlit as st
import cv2
import datetime
import time
import sys
import os
from ultralytics import YOLO
import pandas as pd

# Add src to path
sys.path.append(os.path.dirname(__file__))
from database import save_violation, get_all_violations, get_today_violations, get_violation_counts

# ─── Page Config ───────────────────────────────
st.set_page_config(
    page_title="SafetyEye Dashboard",
    page_icon="👷",
    layout="wide"
)

# ─── Title ─────────────────────────────────────
st.title("SafetyEye - AI Workplace Safety Monitor")
st.markdown("Real-time PPE violation detection system")
st.divider()

# ─── Load Model ────────────────────────────────
@st.cache_resource
def load_model():
    return YOLO("models/best.pt")

model = load_model()

# ─── Class Names ───────────────────────────────
CLASS_NAMES = {
    0: "Hardhat", 1: "Mask", 2: "NO-Hardhat",
    3: "NO-Mask", 4: "NO-Safety Vest", 5: "Person",
    6: "Safety Cone", 7: "Safety Vest",
    8: "Machinery", 9: "Vehicle"
}

VIOLATION_CLASSES = [2, 3, 4]
COOLDOWN_SECONDS = 5

# ─── Sidebar ───────────────────────────────────
st.sidebar.title("Controls")

# Video source selection
source_type = st.sidebar.selectbox(
    "Select Video Source",
    ["Webcam", "Video File", "CCTV/IP Camera"]
)

# Show different input based on selection
if source_type == "Webcam":
    video_source = 0
    st.sidebar.success("Using default webcam")

elif source_type == "Video File":
    uploaded_file = st.sidebar.file_uploader(
        "Upload Video File",
        type=["mp4", "avi", "mov", "mkv"]
    )
    if uploaded_file:
        # Save uploaded file temporarily
        import tempfile
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        video_source = tfile.name
        st.sidebar.success("Video file loaded!")
    else:
        video_source = None
        st.sidebar.warning("Please upload a video file")

elif source_type == "CCTV/IP Camera":
    cctv_url = st.sidebar.text_input(
        "Enter CCTV Stream URL",
        placeholder="rtsp://username:password@ip:port/stream"
    )
    if cctv_url:
        video_source = cctv_url
        st.sidebar.success("CCTV URL set!")
    else:
        video_source = None
        st.sidebar.warning("Please enter CCTV URL")

confidence = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5)
run_detection = st.sidebar.checkbox("Start Detection", value=False)
st.sidebar.divider()
st.sidebar.markdown("### Violation Classes")
st.sidebar.error("NO-Hardhat")
st.sidebar.error("NO-Mask")
st.sidebar.error("NO-Safety Vest")

# ─── Main Layout ───────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live Camera Feed")
    video_placeholder = st.empty()

with col2:
    st.subheader("Live Stats")
    metric1 = st.empty()
    metric2 = st.empty()
    metric3 = st.empty()
    st.divider()
    st.subheader("Recent Alerts")
    alerts_placeholder = st.empty()

st.divider()

# ─── Violation Log Table ───────────────────────
# Charts section
st.divider()
col3, col4 = st.columns(2)

with col3:
    st.subheader("Violations by Type")
    chart_placeholder = st.empty()

with col4:
    st.subheader("Violation Timeline")
    timeline_placeholder = st.empty()

st.divider()
st.subheader("Violation Log")
table_placeholder = st.empty()

# ─── Detection Loop ────────────────────────────
if run_detection:
    if video_source is None:
        st.error("Please select a valid video source!")
        st.stop()
    cap = cv2.VideoCapture(video_source)
    last_alert_time = {}
    session_violations = 0

    while run_detection:
        ret, frame = cap.read()
        if not ret:
            st.error("Camera not found!")
            break

        results = model(frame, conf=confidence, verbose=False)
        recent_alerts = []

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                class_id   = int(box.cls[0])
                conf_score = float(box.conf[0])
                label      = CLASS_NAMES.get(class_id, "Unknown")

                if class_id in VIOLATION_CLASSES:
                    color = (0, 0, 255)
                    current_time = time.time()
                    last_time = last_alert_time.get(class_id, 0)

                    if current_time - last_time >= COOLDOWN_SECONDS:
                        session_violations += 1
                        last_alert_time[class_id] = current_time
                        save_violation(label, conf_score)
                        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                        recent_alerts.append(f"{label} at {timestamp}")
                else:
                    color = (0, 255, 0)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{label} {conf_score:.0%}",
                           (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX,
                           0.6, color, 2)

        # Show frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(frame_rgb, channels="RGB", width=700)

        # Update metrics
        today_violations = get_today_violations()
        metric1.metric("Session Violations", session_violations)
        metric2.metric("Today's Violations", len(today_violations))
        metric3.metric("Status", "MONITORING" if session_violations == 0 else "ALERT!")

        # Show recent alerts
        if recent_alerts:
            alerts_placeholder.error("\n".join(recent_alerts))

        # Update violation log
        # Update violation log
all_violations = get_all_violations()
if all_violations:
    df = pd.DataFrame(all_violations,
                    columns=["ID", "Type", "Confidence",
                            "Timestamp", "Date", "Time"])
    table_placeholder.dataframe(df, use_container_width=True)

    # Bar chart - violations by type
    counts = get_violation_counts()
    if counts:
        count_df = pd.DataFrame(counts,
                               columns=["Violation Type", "Count"])
        chart_placeholder.bar_chart(
            count_df.set_index("Violation Type")
        )

    # Timeline chart
    timeline_df = df[["Time", "Type"]].copy()
    timeline_df["Count"] = 1
    timeline_placeholder.line_chart(
        timeline_df.groupby("Time")["Count"].sum()
    )

    # Stop if checkbox unchecked
    run_detection = st.session_state.get("start_detection", True)

    try:
        cap.release()
    except:
        pass

else:
    video_placeholder.info("Check 'Start Detection' in sidebar to begin monitoring")

    all_violations = get_all_violations()
    if all_violations:
        df = pd.DataFrame(all_violations,
                        columns=["ID", "Type", "Confidence",
                                "Timestamp", "Date", "Time"])
        table_placeholder.dataframe(df, use_container_width=True)

        # Show charts even when not detecting
        counts = get_violation_counts()
        if counts:
            count_df = pd.DataFrame(counts,
                                   columns=["Violation Type", "Count"])
            chart_placeholder.bar_chart(
                count_df.set_index("Violation Type")
            )
    else:
        table_placeholder.info("No violations recorded yet!")
