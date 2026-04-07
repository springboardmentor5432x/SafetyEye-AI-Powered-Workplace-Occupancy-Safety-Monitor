import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
import os
import time

# ==========================================
# PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="SafetyEye AI Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark + Neon Glow CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0d1117;
        color: #e6edf3;
    }

    /* Main Container Glassmorphism */
    .stApp {
        background: radial-gradient(circle at top right, #0d1117, #161b22);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(22, 27, 34, 0.95) !important;
        border-right: 1px solid rgba(48, 54, 61, 0.8);
    }

    /* Glass Cards */
    .metric-card {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(48, 54, 61, 0.8);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #58a6ff;
        box-shadow: 0 8px 24px rgba(88, 166, 255, 0.15);
    }

    /* Neon Borders for Feed */
    .video-container {
        border: 2px solid #238636;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(35, 134, 54, 0.2);
    }
    .alert-container {
        border: 1px solid #da3633;
        background: rgba(218, 54, 51, 0.05);
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }

    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 8px;
    }
    .status-active { background: rgba(35, 134, 54, 0.2); color: #3fb950; border: 1px solid #238636; }
    .status-system { background: rgba(137, 87, 229, 0.2); color: #bc8cff; border: 1px solid #8957e5; }

    /* Hide Default Navigation */
    div[data-testid="stSidebarNav"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'source' not in st.session_state:
    st.session_state.source = "Dashboard"

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("## 🛡️ SafetyEye")
    st.markdown("---")
    
    st.session_state.source = st.radio(
        "NAVIGATION",
        ["Dashboard", "Webcam Monitoring", "Video Testing"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### CONTROLS")
    
    # Toggle logic
    start_btn = st.toggle("Start Monitoring", value=st.session_state.monitoring)
    st.session_state.monitoring = start_btn
    
    if st.button("Stop", use_container_width=True, type="secondary"):
        st.session_state.monitoring = False
        st.rerun()

    st.markdown("---")
    
    # Video Input Selection (Only for Video Testing)
    selected_video = None
    camera_index = 0
    if st.session_state.source == "Video Testing":
        video_files = [f for f in os.listdir("dataset/videos") if f.endswith(('.mp4', '.avi'))]
        selected_video = st.selectbox("Select Video File", video_files) if video_files else None
    elif st.session_state.source == "Webcam Monitoring":
        camera_index = st.selectbox("Select Camera Index", [0, 1, 2], index=0)

# ==========================================
# MODEL LOADING
# ==========================================
@st.cache_resource
def load_yolo_model():
    return YOLO("models/bestmodel.pt")

model = load_yolo_model()

# ==========================================
# DETECTION ENGINE
# ==========================================
def process_frame(frame):
    # Resize for performance (Standard resolution for YOLO input)
    frame = cv2.resize(frame, (640, 480))
    results = model(frame, conf=0.5, verbose=False)
    
    alerts = []
    person_count = 0
    unsafe_count = 0
    
    annotated_frame = frame.copy()
    
    for r in results:
        boxes = r.boxes
        persons = []
        equipment = [] # (label, (x1, y1, x2, y2))

        for box in boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            xyxy = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            
            if label == "Person":
                persons.append(xyxy)
                person_count += 1
            else:
                equipment.append((label, xyxy))

        # Core logic: Equipment inside person bounding box
        for px1, py1, px2, py2 in persons:
            has_hardhat = False
            has_vest = False
            has_mask = False
            
            for eq_label, (ex1, ey1, ex2, ey2) in equipment:
                # Check overlap (Heuristic: Equipment centroid or majority inside person bbox)
                if ex1 > px1 - 20 and ey1 > py1 - 20 and ex2 < px2 + 20 and ey2 < py2 + 20:
                    if eq_label == "Hardhat": has_hardhat = True
                    if eq_label == "Safety Vest": has_vest = True
                    if eq_label == "Mask": has_mask = True
            
            is_unsafe = not (has_hardhat and has_vest) # Mask Optional for some PPE definitions, but let's stick to requirements
            # The prompt mentions checking all: Helmet, Mask, Safety Vest
            if not has_mask: is_unsafe = True

            color = (0, 255, 0) # Green for Safe
            status_text = "SAFE"
            
            if is_unsafe:
                unsafe_count += 1
                color = (0, 0, 255) # Red for Unsafe
                status_text = "UNSAFE"
                
                missing = []
                if not has_hardhat: missing.append("Helmet")
                if not has_vest: missing.append("Safety Vest")
                if not has_mask: missing.append("Mask")
                
                for item in missing:
                    alerts.append(f"VIOLATION: {item} Missing")

            # Draw person box
            cv2.rectangle(annotated_frame, (int(px1), int(py1)), (int(px2), int(py2)), color, 2)
            cv2.putText(annotated_frame, f"{status_text}", (int(px1), int(py1) - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # (Equipment box drawing removed for clean UI)

    return annotated_frame, list(set(alerts)), person_count, unsafe_count

# ==========================================
# MAIN DASHBOARD UI
# ==========================================
def main():
    # Header Section
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
            <div>
                <h1 style='margin-bottom:0;'>SafetyEye AI Dashboard</h1>
                <p style='color:#8b949e;'>Real-Time Workplace Safety Monitoring System</p>
            </div>
            <div>
                <span class="status-badge status-system">SYSTEM RUNNING</span>
                <span class="status-badge status-active">AI CORE: ACTIVE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Metrics Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    # Initialize placeholders immediately to prevent background duplication
    metrics_placeholders = [m_col1.empty(), m_col2.empty(), m_col3.empty(), m_col4.empty()]
    
    # Initial state for metrics
    metrics_placeholders[0].markdown(f"""<div class="metric-card"><h3>👥 Total Persons</h3><h2 style="color:#58a6ff;">0</h2></div>""", unsafe_allow_html=True)
    metrics_placeholders[1].markdown(f"""<div class="metric-card"><h3>⚠️ Unsafe Workers</h3><h2 style="color:#f85149;">0</h2></div>""", unsafe_allow_html=True)
    metrics_placeholders[2].markdown(f"""<div class="metric-card"><h3>🚨 Alerts Count</h3><h2 style="color:#d29922;">0</h2></div>""", unsafe_allow_html=True)
    metrics_placeholders[3].markdown(f"""<div class="metric-card"><h3>📷 Camera Status</h3><h2 style="color:#3fb950;">Active</h2></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Content Area
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown(f"### Live Monitoring Feed ({st.session_state.source})")
        feed_placeholder = st.empty()
        # Initial placeholder image
        feed_placeholder.image(np.zeros((360, 480, 3)), channels="RGB", use_container_width=True)

    with col_right:
        st.markdown("### Live Alerts & Violations")
        alert_placeholder = st.empty()
        with alert_placeholder.container():
            st.success("✅ SYSTEM STATUS: ALL SAFE")

    # MONITORING LOOP
    if st.session_state.monitoring:
        try:
            # Handle source
            if st.session_state.source == "Webcam Monitoring":
                cap = cv2.VideoCapture(camera_index)
            elif st.session_state.source == "Video Testing" and selected_video:
                cap = cv2.VideoCapture(os.path.join("dataset/videos", selected_video))
            else:
                st.warning("Please select a video file or choose Webcam.")
                st.session_state.monitoring = False
                return

            if not cap.isOpened():
                st.error(f"Failed to open source (Index: {camera_index if st.session_state.source == 'Webcam Monitoring' else selected_video}).")
                st.session_state.monitoring = False
                return

            while st.session_state.monitoring:
                ret, frame = cap.read()
                if not ret:
                    if st.session_state.source == "Video Testing":
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Loop video
                        continue
                    break
                
                # Inference
                p_frame, alerts, p_count, u_count = process_frame(frame)
                p_frame_rgb = cv2.cvtColor(p_frame, cv2.COLOR_BGR2RGB)
                
                # Update UI
                feed_placeholder.image(p_frame_rgb, use_container_width=True)
                
                # Update Metrics
                metrics_placeholders[0].markdown(f"""<div class="metric-card"><h3>👥 Total Persons</h3><h2 style="color:#58a6ff;">{p_count}</h2></div>""", unsafe_allow_html=True)
                metrics_placeholders[1].markdown(f"""<div class="metric-card"><h3>⚠️ Unsafe Workers</h3><h2 style="color:#f85149;">{u_count}</h2></div>""", unsafe_allow_html=True)
                metrics_placeholders[2].markdown(f"""<div class="metric-card"><h3>🚨 Alerts Count</h3><h2 style="color:#d29922;">{len(alerts)}</h2></div>""", unsafe_allow_html=True)

                # Update Alerts
                if not alerts:
                    alert_placeholder.success("✅ SYSTEM STATUS: ALL SAFE")
                else:
                    # Build string for current frame only
                    alert_html = "".join([f'<div class="alert-container">❌ {alert}</div>' for alert in alerts])
                    alert_placeholder.markdown(alert_html, unsafe_allow_html=True)

                time.sleep(0.01) # Small delay for UI smoothness

            cap.release()
        except Exception as e:
            st.error(f"Error: {e}")
            st.session_state.monitoring = False
    else:
        st.info("Monitoring is currently OFF. Use the sidebar toggle to start.")

if __name__ == "__main__":
    main()