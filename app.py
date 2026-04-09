#SafetyEye - Optimized Dashboard

# Standard library imports
import os
import time
import threading
from datetime import datetime
import av
import cv2
import pandas as pd
import plotly.express as px
import streamlit as st
from ultralytics import YOLO
from streamlit_webrtc import WebRtcMode, webrtc_streamer

# Configure the Streamlit page
st.set_page_config(
    page_title="SafetyEye Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a cleaner dashboard look
st.markdown(
    """
    <style>
        .main { padding-top: 1rem; }
        .hero-box {
            padding: 18px 22px;
            border-radius: 18px;
            background: linear-gradient(135deg, #101828 0%, #1f2937 100%);
            color: white;
            margin-bottom: 12px;
            border: 1px solid rgba(255,255,255,0.08);
        }
        .hero-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .hero-subtitle {
            opacity: 0.85;
            font-size: 1rem;
        }
        .soft-card {
            padding: 14px 16px;
            border-radius: 16px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">SafetyEye Dashboard</div>
        <div class="hero-subtitle">AI-powered workplace occupancy and PPE compliance monitor</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Project file locations
MODEL_PATH = "models/best.pt"
LOG_FILE = "violations.csv"
SCREENSHOT_DIR = "violation_screenshots"
TEMP_VIDEO_DIR = "temp_streams"

# Class names expected from the trained YOLO model
PERSON_CLASS = "Person"
HELMET_CLASS = "Hardhat"
VEST_CLASS = "Safety Vest"
NEG_HELMET_CLASS = "NO-Hardhat"
NEG_VEST_CLASS = "NO-Safety Vest"

# Colors used for drawing detection boxes
CLASS_COLORS = {
    PERSON_CLASS: (180, 180, 180),
    HELMET_CLASS: (0, 220, 0),
    VEST_CLASS: (0, 180, 255),
    NEG_HELMET_CLASS: (0, 0, 255),
    NEG_VEST_CLASS: (0, 0, 220),
}
DEFAULT_COLOR = (220, 220, 220)

# STUN server config for webcam streaming
RTC_CONFIGURATION = {
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
}

# Create required folders/files if they do not exist yet
def ensure_project_files():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(TEMP_VIDEO_DIR, exist_ok=True)
    if not os.path.exists(LOG_FILE):
        pd.DataFrame(
            columns=["timestamp", "violation_type", "confidence", "source", "screenshot"]
        ).to_csv(LOG_FILE, index=False)

ensure_project_files()

# Default values stored in Streamlit session state
STATE_DEFAULTS = {
    "video_running": False,
    "video_cap": None,
    "video_source_name": "",
    "video_temp_path": "",
    "video_frame_count": 0,
    "video_fps_start_time": time.time(),
    "video_fps_value": 0.0,
    "video_last_log_times": {},
    "video_last_detections": [],
    "video_people_now": 0,
    "video_compliance_now": 100.0,
    "video_alerts_now": [],
    "video_last_screenshot": "",
}

for key, value in STATE_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Load the model only once and keep it cached
@st.cache_resource
def load_model(model_path: str):
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found: {model_path}. Place best.pt in the same folder as app.py."
        )
    return YOLO(model_path)

model = load_model(MODEL_PATH)

# Read the CSV log file safely
def load_logs() -> pd.DataFrame:
    try:
        return pd.read_csv(LOG_FILE)
    except Exception:
        return pd.DataFrame(
            columns=["timestamp", "violation_type", "confidence", "source", "screenshot"]
        )

# Add a new violation entry to the CSV log
def append_log(violation_type: str, confidence: float, source: str, screenshot_path: str):
    row = pd.DataFrame([{
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "violation_type": violation_type,
        "confidence": round(float(confidence), 3),
        "source": source,
        "screenshot": screenshot_path,
    }])
    row.to_csv(LOG_FILE, mode="a", header=False, index=False)

# Save a frame image when a violation is detected
def save_screenshot(frame, violation_type: str) -> str:
    safe_name = violation_type.replace(" ", "_").replace("/", "_")
    time_tag = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{time_tag}_{safe_name}.jpg"
    path = os.path.join(SCREENSHOT_DIR, filename)
    cv2.imwrite(path, frame)
    return path

# Save the uploaded video to a temporary folder for processing
def save_uploaded_video(uploaded_file) -> str:
    safe_name = uploaded_file.name.replace(" ", "_")
    save_path = os.path.join(TEMP_VIDEO_DIR, safe_name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())
    return save_path

# Count total violations and category-wise violations
def compute_log_summary(df: pd.DataFrame):
    if df.empty:
        return 0, 0, 0
    hardhat_count = df["violation_type"].astype(str).str.contains("Hardhat", case=False, na=False).sum()
    vest_count = df["violation_type"].astype(str).str.contains("Vest", case=False, na=False).sum()
    total_count = len(df)
    return int(total_count), int(hardhat_count), int(vest_count)

# Prepare bar chart data for violation types
def build_type_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["violation_type", "count"])
    return (
        df.groupby("violation_type")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

# Prepare line chart data showing violations over time
def build_time_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["minute", "count"])
    temp = df.copy()
    temp["timestamp"] = pd.to_datetime(temp["timestamp"], errors="coerce")
    temp = temp.dropna(subset=["timestamp"])
    if temp.empty:
        return pd.DataFrame(columns=["minute", "count"])
    temp["minute"] = temp["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    return temp.groupby("minute").size().reset_index(name="count")

# Resize frames to reduce processing load while keeping aspect ratio
def resize_frame_keep_ratio(frame, target_width: int):
    h, w = frame.shape[:2]
    if w <= target_width:
        return frame
    scale = target_width / float(w)
    new_h = int(h * scale)
    return cv2.resize(frame, (target_width, new_h))

# Compute intersection-over-union for two bounding boxes
def calculate_iou(box_a, box_b) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    iw = max(0, ix2 - ix1)
    ih = max(0, iy2 - iy1)
    intersection = iw * ih
    if intersection == 0:
        return 0.0
    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    union = area_a + area_b - intersection
    return intersection / union if union > 0 else 0.0

# Check whether a detected helmet belongs to a detected person
def helmet_matches_person(person_box, helmet_box, min_iou=0.05) -> bool:
    if calculate_iou(person_box, helmet_box) >= min_iou:
        return True
    px1, py1, px2, py2 = person_box
    hx1, hy1, hx2, hy2 = helmet_box
    helmet_cx = (hx1 + hx2) / 2
    helmet_cy = (hy1 + hy2) / 2
    person_h = py2 - py1
    upper_limit = py1 + 0.45 * person_h
    return px1 <= helmet_cx <= px2 and py1 <= helmet_cy <= upper_limit

# Check whether a detected safety vest belongs to a detected person
def vest_matches_person(person_box, vest_box, min_iou=0.05) -> bool:
    if calculate_iou(person_box, vest_box) >= min_iou:
        return True
    px1, py1, px2, py2 = person_box
    vx1, vy1, vx2, vy2 = vest_box
    vest_cx = (vx1 + vx2) / 2
    vest_cy = (vy1 + vy2) / 2
    person_h = py2 - py1
    top_limit = py1 + 0.20 * person_h
    bottom_limit = py1 + 0.85 * person_h
    return px1 <= vest_cx <= px2 and top_limit <= vest_cy <= bottom_limit

# Convert raw YOLO output into a simple Python list of detections
def parse_detections(result) -> list:
    detections = []
    if result.boxes is None:
        return detections
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        label = result.names[class_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        detections.append({
            "label": label,
            "confidence": confidence,
            "box": [x1, y1, x2, y2],
        })
    return detections

# Decide active violations and calculate compliance statistics for the frame
def evaluate_frame(detections: list):
    persons = [d for d in detections if d["label"] == PERSON_CLASS]
    helmets = [d for d in detections if d["label"] == HELMET_CLASS]
    vests = [d for d in detections if d["label"] == VEST_CLASS]
    direct_violations = []
    for d in detections:
        if d["label"] == NEG_HELMET_CLASS:
            direct_violations.append("Missing Hardhat")
        elif d["label"] == NEG_VEST_CLASS:
            direct_violations.append("Missing Safety Vest")
    inferred_violations = []
    compliant_people = 0
    for person in persons:
        person_box = person["box"]
        has_helmet = any(helmet_matches_person(person_box, helmet["box"]) for helmet in helmets)
        has_vest = any(vest_matches_person(person_box, vest["box"]) for vest in vests)
        if has_helmet and has_vest:
            compliant_people += 1
        else:
            if not has_helmet:
                inferred_violations.append("Missing Hardhat")
            if not has_vest:
                inferred_violations.append("Missing Safety Vest")
    active_violations = sorted(set(direct_violations + inferred_violations))
    people_count = len(persons)
    compliance_pct = 100.0 if people_count == 0 else (compliant_people / people_count) * 100.0
    return active_violations, people_count, compliant_people, compliance_pct

# Draw boxes, labels and status text on the frame
def draw_overlay(frame, detections, active_violations, people_count, compliance_pct, fps_value):
    output = frame.copy()
    for det in detections:
        label = det["label"]
        conf = det["confidence"]
        x1, y1, x2, y2 = det["box"]
        color = CLASS_COLORS.get(label, DEFAULT_COLOR)
        cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
        text = f"{label} {conf:.2f}"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
        cv2.rectangle(output, (x1, max(0, y1 - th - 8)), (x1 + tw + 4, y1), color, -1)
        cv2.putText(output, text, (x1 + 2, max(12, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 0), 1)
    cv2.rectangle(output, (0, 0), (250, 82), (20, 20, 20), -1)
    cv2.putText(output, f"FPS: {fps_value:.1f}", (10, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
    cv2.putText(output, f"People: {people_count}", (10, 47), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
    cv2.putText(output, f"Compliance: {compliance_pct:.1f}%", (10, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
    if active_violations:
        warning_text = " | ".join(active_violations[:2])
        cv2.rectangle(output, (0, 90), (output.shape[1], 118), (0, 0, 210), -1)
        cv2.putText(output, f"WARNING: {warning_text}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2)
    return output

# Stop uploaded video processing and reset related state values
def stop_video_file():
    cap = st.session_state.get("video_cap")
    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass
    st.session_state.video_running = False
    st.session_state.video_cap = None
    st.session_state.video_frame_count = 0
    st.session_state.video_fps_start_time = time.time()
    st.session_state.video_fps_value = 0.0
    st.session_state.video_last_detections = []
    st.session_state.video_people_now = 0
    st.session_state.video_compliance_now = 100.0
    st.session_state.video_alerts_now = []

# Start processing a newly uploaded video file
def start_video_file(uploaded_video):
    stop_video_file()
    if uploaded_video is None:
        st.sidebar.error("Please upload a video first.")
        return
    video_path = save_uploaded_video(uploaded_video)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.sidebar.error("Could not open uploaded video.")
        return
    st.session_state.video_running = True
    st.session_state.video_cap = cap
    st.session_state.video_source_name = uploaded_video.name
    st.session_state.video_temp_path = video_path
    st.session_state.video_frame_count = 0
    st.session_state.video_fps_start_time = time.time()
    st.session_state.video_fps_value = 0.0
    st.session_state.video_last_log_times = {}
    st.session_state.video_last_detections = []
    st.session_state.video_people_now = 0
    st.session_state.video_compliance_now = 100.0
    st.session_state.video_alerts_now = []

# Video processor used by streamlit-webrtc for webcam detection
class SafetyVideoProcessor:
    def __init__(self, confidence, process_width, process_every_n, log_cooldown, device_choice):
        self.confidence = confidence
        self.process_width = process_width
        self.process_every_n = max(1, int(process_every_n))
        self.log_cooldown = log_cooldown
        self.device_choice = None if device_choice == "auto" else device_choice
        self.lock = threading.Lock()
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.fps_value = 0.0
        self.last_detections = []
        self.last_log_times = {}
        self.snapshot = {"people": 0, "compliance": 100.0, "alerts": [], "fps": 0.0}

    # Process each incoming webcam frame
    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")
        image = resize_frame_keep_ratio(image, self.process_width)
        self.frame_count += 1
        elapsed = time.time() - self.fps_start_time
        if elapsed > 0:
            self.fps_value = self.frame_count / elapsed
        run_inference_now = (self.frame_count % self.process_every_n == 0 or not self.last_detections)
        if run_inference_now:
            result = model.predict(
                image, conf=self.confidence, imgsz=self.process_width, verbose=False, device=self.device_choice
            )[0]
            detections = parse_detections(result)
            self.last_detections = detections
        else:
            detections = self.last_detections
        active_violations, people_count, compliant_people, compliance_pct = evaluate_frame(detections)
        annotated = draw_overlay(image, detections, active_violations, people_count, compliance_pct, self.fps_value)
        best_conf = max([d["confidence"] for d in detections], default=0.0)
        now = time.time()
        for violation in active_violations:
            last_time = self.last_log_times.get(violation, 0)
            if now - last_time >= self.log_cooldown:
                screenshot_path = save_screenshot(annotated, violation)
                append_log(violation, best_conf, "webcam", screenshot_path)
                self.last_log_times[violation] = now
        with self.lock:
            self.snapshot = {
                "people": people_count,
                "compliance": compliance_pct,
                "alerts": active_violations,
                "fps": self.fps_value,
            }
        return av.VideoFrame.from_ndarray(annotated, format="bgr24")

# Sidebar navigation between dashboard pages
page = st.sidebar.radio("Go to", ["Live Monitoring", "Analytics", "Violation Logs"])

st.sidebar.markdown("### Source")
source_mode = st.sidebar.selectbox("Detection Source", ["Webcam", "Video File"])

# Show video uploader only when video file mode is selected
uploaded_video = None
if source_mode == "Video File":
    uploaded_video = st.sidebar.file_uploader("Upload a video", type=["mp4", "avi", "mov"])

# Controls that affect speed and detection quality
st.sidebar.markdown("### Performance")
confidence_threshold = st.sidebar.slider("Detection confidence", 0.10, 0.95, 0.40, 0.05)
processing_width = st.sidebar.slider("Processing width", 480, 960, 640, 32)
process_every_n = st.sidebar.slider("Run model every N frames", 1, 5, 3, 1)
log_cooldown = st.sidebar.slider("Log cooldown (seconds)", 1, 15, 5, 1)
refresh_delay = st.sidebar.slider("Video file refresh delay", 0.03, 0.20, 0.06, 0.01)
device_choice = st.sidebar.selectbox("Inference device", ["auto", "cpu", "mps"], index=0)

st.sidebar.caption("Use 'mps' only on Apple Silicon. Use 'cpu' if you get device errors.")

# Manual controls for uploaded video playback
if source_mode == "Video File":
    st.sidebar.markdown("### Video Controls")
    start_video = st.sidebar.button("Start Video Detection", use_container_width=True)
    stop_video = st.sidebar.button("Stop Video Detection", use_container_width=True)
    if start_video:
        start_video_file(uploaded_video)
        st.rerun()
    if stop_video:
        stop_video_file()
        st.rerun()
else:
    if st.session_state.video_running:
        stop_video_file()

# Main live monitoring page
if page == "Live Monitoring":
    st.subheader("Live Monitoring Feed")
    left_col, right_col = st.columns([1.7, 1.0])

    with left_col:
        # Webcam mode uses streamlit-webrtc for smoother live streaming
        if source_mode == "Webcam":
            st.info("Use START / STOP inside the webcam box below.")

            def processor_factory():
                return SafetyVideoProcessor(
                    confidence=confidence_threshold,
                    process_width=processing_width,
                    process_every_n=process_every_n,
                    log_cooldown=log_cooldown,
                    device_choice=device_choice,
                )

            ctx = webrtc_streamer(
                key="safetyeye-webcam",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration=RTC_CONFIGURATION,
                media_stream_constraints={"video": True, "audio": False},
                async_processing=True,
                video_processor_factory=processor_factory,
            )
        else:
            # Video file mode reads frames from the uploaded file
            frame_placeholder = st.empty()
            if not st.session_state.video_running:
                frame_placeholder.info("Upload a video and click 'Start Video Detection' from the sidebar.")
            else:
                cap = st.session_state.video_cap
                if cap is None:
                    frame_placeholder.warning("Video source is not open.")
                else:
                    status_box = right_col.empty()
                    video_fps = cap.get(cv2.CAP_PROP_FPS)
                    frame_delay = 1.0 / video_fps if video_fps and video_fps > 1 else refresh_delay

                    while st.session_state.video_running:
                        success, frame = cap.read()
                        if not success:
                            frame_placeholder.warning("Video ended.")
                            stop_video_file()
                            break

                        # Keep track of processed frames for FPS calculation
                        st.session_state.video_frame_count += 1
                        elapsed = time.time() - st.session_state.video_fps_start_time
                        if elapsed > 0:
                            st.session_state.video_fps_value = st.session_state.video_frame_count / elapsed

                        # Resize the frame before running detection
                        frame = resize_frame_keep_ratio(frame, processing_width)
                        # Run YOLO only on selected frames to improve speed
                        run_inference_now = (
                            st.session_state.video_frame_count % process_every_n == 0
                            or not st.session_state.video_last_detections
                        )

                        if run_inference_now:
                            result = model.predict(
                                frame,
                                conf=confidence_threshold,
                                imgsz=processing_width,
                                verbose=False,
                                device=None if device_choice == "auto" else device_choice,
                            )[0]
                            detections = parse_detections(result)
                            st.session_state.video_last_detections = detections
                        else:
                            detections = st.session_state.video_last_detections

                        # Evaluate PPE compliance for the current frame
                        active_violations, people_count, compliant_people, compliance_pct = evaluate_frame(detections)
                        st.session_state.video_people_now = people_count
                        st.session_state.video_compliance_now = compliance_pct
                        st.session_state.video_alerts_now = active_violations

                        annotated = draw_overlay(
                            frame,
                            detections,
                            active_violations,
                            people_count,
                            compliance_pct,
                            st.session_state.video_fps_value,
                        )

                        best_conf = max([d["confidence"] for d in detections], default=0.0)
                        now = time.time()
                        # Save logs/screenshots with cooldown to avoid duplicate spam
                        for violation in active_violations:
                            last_time = st.session_state.video_last_log_times.get(violation, 0)
                            if now - last_time >= log_cooldown:
                                screenshot_path = save_screenshot(annotated, violation)
                                append_log(
                                    violation_type=violation,
                                    confidence=best_conf,
                                    source=st.session_state.video_source_name,
                                    screenshot_path=screenshot_path,
                                )
                                st.session_state.video_last_log_times[violation] = now
                                st.session_state.video_last_screenshot = screenshot_path

                        frame_placeholder.image(annotated, channels="BGR", use_container_width=True)

                        with status_box.container():
                            st.markdown('<div class="soft-card">', unsafe_allow_html=True)
                            st.markdown("### Current Status")
                            st.write(f"**Source:** {st.session_state.video_source_name}")
                            st.write(f"**People in frame:** {st.session_state.video_people_now}")
                            st.write(f"**Current compliance:** {st.session_state.video_compliance_now:.1f}%")
                            st.write(f"**FPS:** {st.session_state.video_fps_value:.1f}")
                            if st.session_state.video_alerts_now:
                                st.error("Active alerts: " + ", ".join(st.session_state.video_alerts_now))
                            else:
                                st.success("No active alerts")
                            c1, c2, c3, c4 = st.columns(4)
                            c1.metric("People", st.session_state.video_people_now)
                            c2.metric("Compliance", f"{st.session_state.video_compliance_now:.1f}%")
                            c3.metric("FPS", f"{st.session_state.video_fps_value:.1f}")
                            c4.metric("Alerts", len(st.session_state.video_alerts_now))
                            st.markdown('</div>', unsafe_allow_html=True)

                        time.sleep(max(refresh_delay, frame_delay * 0.5))

    # Right side panel shows current status and metrics
    with right_col:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown("### Current Status")
        # Webcam mode uses streamlit-webrtc for smoother live streaming
        if source_mode == "Webcam":
            if "ctx" in locals() and ctx.state.playing and ctx.video_processor:
                # Read the latest webcam stats safely from the processor
                with ctx.video_processor.lock:
                    snap = ctx.video_processor.snapshot.copy()
                people_now = snap.get("people", 0)
                compliance_now = snap.get("compliance", 100.0)
                alerts_now = snap.get("alerts", [])
                fps_now = snap.get("fps", 0.0)
                st.write("**Source:** webcam")
                st.write(f"**People in frame:** {people_now}")
                st.write(f"**Current compliance:** {compliance_now:.1f}%")
                st.write(f"**FPS:** {fps_now:.1f}")
                if alerts_now:
                    st.error("Active alerts: " + ", ".join(alerts_now))
                else:
                    st.success("No active alerts")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("People", people_now)
                c2.metric("Compliance", f"{compliance_now:.1f}%")
                c3.metric("FPS", f"{fps_now:.1f}")
                c4.metric("Alerts", len(alerts_now))
            else:
                st.write("**Source:** webcam")
                st.info("Webcam is not running.")
        else:
            if not st.session_state.video_running:
                st.write("**Source:** Stopped")
                st.write(f"**People in frame:** {st.session_state.video_people_now}")
                st.write(f"**Current compliance:** {st.session_state.video_compliance_now:.1f}%")
                st.write(f"**FPS:** {st.session_state.video_fps_value:.1f}")
                if st.session_state.video_alerts_now:
                    st.error("Active alerts: " + ", ".join(st.session_state.video_alerts_now))
                else:
                    st.success("No active alerts")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("People", st.session_state.video_people_now)
                c2.metric("Compliance", f"{st.session_state.video_compliance_now:.1f}%")
                c3.metric("FPS", f"{st.session_state.video_fps_value:.1f}")
                c4.metric("Alerts", len(st.session_state.video_alerts_now))
            else:
                st.info("Video file status is updating beside the feed.")
        st.markdown('</div>', unsafe_allow_html=True)

# Analytics page
elif page == "Analytics":
    st.subheader("Analytics")
    logs_df = load_logs()
    total_logged, hardhat_logged, vest_logged = compute_log_summary(logs_df)
    a1, a2, a3 = st.columns(3)
    a1.metric("Total Violations", total_logged)
    a2.metric("Hardhat Violations", hardhat_logged)
    a3.metric("Vest Violations", vest_logged)
    chart_left, chart_right = st.columns(2)
    with chart_left:
        st.markdown("### Violations by Type")
        type_df = build_type_chart_data(logs_df)
        if type_df.empty:
            st.info("No violation data available.")
        else:
            fig_bar = px.bar(type_df, x="violation_type", y="count", text="count")
            fig_bar.update_layout(margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)
    with chart_right:
        st.markdown("### Violations Over Time")
        time_df = build_time_chart_data(logs_df)
        if time_df.empty:
            st.info("No trend data available.")
        else:
            fig_line = px.line(time_df, x="minute", y="count", markers=True)
            fig_line.update_layout(margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_line, use_container_width=True)

# Violation log page
elif page == "Violation Logs":
    st.subheader("Violation Logs")
    logs_df = load_logs()
    latest_screenshot = ""
    if not logs_df.empty and "screenshot" in logs_df.columns:
        valid_shots = logs_df["screenshot"].dropna().astype(str)
        valid_shots = valid_shots[valid_shots != ""]
        if len(valid_shots) > 0:
            latest_screenshot = valid_shots.iloc[-1]
    left_box, right_box = st.columns([1.1, 1.7])
    with left_box:
        st.markdown("### Latest Evidence")
        if latest_screenshot and os.path.exists(latest_screenshot):
            st.image(latest_screenshot, use_container_width=True)
            st.caption(os.path.basename(latest_screenshot))
        else:
            st.info("No evidence screenshot available yet.")
    with right_box:
        st.markdown("### Recent Logs")
        if logs_df.empty:
            st.info("No logs found.")
        else:
            search_text = st.text_input("Search violation type", "")
            filtered_df = logs_df.copy()
            if search_text.strip():
                filtered_df = filtered_df[
                    filtered_df["violation_type"].astype(str).str.contains(search_text, case=False, na=False)
                ]
            st.dataframe(
                filtered_df.iloc[::-1].reset_index(drop=True),
                use_container_width=True,
                hide_index=True,
            )
            st.download_button(
                "Download CSV",
                data=filtered_df.to_csv(index=False),
                file_name="violations_export.csv",
                mime="text/csv",
            )
