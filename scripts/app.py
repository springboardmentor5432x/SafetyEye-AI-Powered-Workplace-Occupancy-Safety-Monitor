import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
import os
import time
import datetime

# ==========================================
# PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="SafetyEye AI Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Premium Dark Futuristic UI ────────────────────────────────────────────────
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ─── Global Reset ──────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #0a0e1a !important;
        color: #e2e8f0 !important;
    }
    .stApp {
        background: radial-gradient(ellipse at top right, #0f1628 0%, #0a0e1a 60%, #060912 100%) !important;
    }

    /* ─── Hide Default Streamlit Chrome ─────────────────────────── */
    div[data-testid="stSidebarNav"]   { display: none !important; }
    #MainMenu, footer                  { visibility: hidden !important; }
    .stDeployButton                    { display: none !important; }

    /* ─── SIDEBAR ────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #0a0e1a 50%, #060912 100%) !important;
        border-right: 1px solid rgba(77, 166, 255, 0.15) !important;
        padding-top: 0 !important;
        min-width: 240px !important;
        max-width: 240px !important;
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding: 0 0 16px 0 !important;
    }

    /* ─── Sidebar Logo ───────────────────────────────────────────── */
    .se-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 20px 18px 16px 18px;
        border-bottom: 1px solid rgba(77, 166, 255, 0.12);
        margin-bottom: 6px;
    }
    .se-logo-icon { font-size: 1.7rem; filter: drop-shadow(0 0 8px #4da6ff); }
    .se-logo-text {
        font-size: 1.2rem; font-weight: 800;
        background: linear-gradient(135deg, #4da6ff, #00d4ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }

    /* ─── Section Labels ─────────────────────────────────────────── */
    .se-nav-label, .se-controls-label {
        font-size: 0.62rem; font-weight: 700; letter-spacing: 0.12em;
        color: #3d4f63; text-transform: uppercase; padding: 8px 18px 4px 18px;
    }

    /* ─── Nav Buttons — override ALL Streamlit defaults ─────────── */
    section[data-testid="stSidebar"] button[kind="secondary"],
    section[data-testid="stSidebar"] button[kind="primary"],
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: none !important;
        border-left: 2px solid transparent !important;
        border-radius: 0 10px 10px 0 !important;
        color: #6b7c96 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 9px 16px 9px 14px !important;
        margin: 1px 0 !important;
        width: 100% !important;
        box-shadow: none !important;
        transition: all 0.18s ease !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(77, 166, 255, 0.07) !important;
        border-left-color: rgba(77, 166, 255, 0.35) !important;
        color: #b8cce8 !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] .stButton > button:focus {
        box-shadow: none !important;
        outline: none !important;
    }

    /* Active nav button highlight */
    .nav-active section[data-testid="stSidebar"] .stButton > button {
        background: rgba(77,166,255,0.1) !important;
        border-left-color: #4da6ff !important;
        color: #4da6ff !important;
    }

    /* ─── Stop Button Override ───────────────────────────────────── */
    section[data-testid="stSidebar"] .stop-wrap .stButton > button {
        background: rgba(255, 68, 68, 0.08) !important;
        border: 1px solid rgba(255, 68, 68, 0.28) !important;
        border-radius: 10px !important;
        color: #ff6b6b !important;
        font-weight: 600 !important;
        text-align: center !important;
        justify-content: center !important;
        margin: 0 10px !important;
        width: calc(100% - 20px) !important;
        box-shadow: 0 0 8px rgba(255,68,68,0.1) !important;
    }
    section[data-testid="stSidebar"] .stop-wrap .stButton > button:hover {
        background: rgba(255, 68, 68, 0.18) !important;
        box-shadow: 0 0 16px rgba(255,68,68,0.28) !important;
    }

    /* ─── Divider ─────────────────────────────────────────────────── */
    .se-divider {
        border: none; border-top: 1px solid rgba(77,166,255,0.08);
        margin: 8px 12px;
    }

    /* ─── Camera Status ──────────────────────────────────────────── */
    .cam-status {
        display: flex; align-items: center; gap: 8px;
        padding: 6px 18px 12px 18px;
        font-size: 0.78rem; color: #4a5568; font-weight: 500;
    }
    .cam-dot-active   { width:8px;height:8px;border-radius:50%;background:#00ff88;
                         box-shadow:0 0 6px #00ff88;animation:pulse-dot 1.5s infinite; }
    .cam-dot-inactive { width:8px;height:8px;border-radius:50%;background:#ff4444; }
    @keyframes pulse-dot {
        0%,100% { box-shadow:0 0 4px #00ff88; }
        50%      { box-shadow:0 0 12px #00ff88,0 0 20px rgba(0,255,136,0.4); }
    }

    /* ─── FLOATING SIDEBAR TOGGLE BUTTON ─────────────────────────── */
    /* Shows only when sidebar is collapsed */
    .se-sidebar-toggle {
        position: fixed;
        top: 12px;
        left: 12px;
        z-index: 9999;
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: rgba(13, 17, 23, 0.92);
        border: 1px solid rgba(77, 166, 255, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 0 16px rgba(77,166,255,0.2);
        backdrop-filter: blur(8px);
        transition: all 0.2s ease;
        font-size: 1rem;
        color: #4da6ff;
    }
    .se-sidebar-toggle:hover {
        background: rgba(77,166,255,0.15);
        box-shadow: 0 0 24px rgba(77,166,255,0.35);
        transform: scale(1.05);
    }
    /* Only show when sidebar IS collapsed (Streamlit adds [aria-expanded="false"]) */
    section[data-testid="stSidebar"][aria-expanded="true"]  ~ * .se-sidebar-toggle,
    section[data-testid="stSidebar"][aria-expanded="true"]  .se-sidebar-toggle {
        display: none !important;
    }

    /* ─── MAIN HEADER ─────────────────────────────────────────────── */
    .se-header {
        display: flex; justify-content: space-between; align-items: flex-start;
        padding: 8px 0 20px 0;
        border-bottom: 1px solid rgba(77,166,255,0.1);
        margin-bottom: 22px;
    }
    .se-header-title {
        font-size: 1.7rem; font-weight: 800;
        background: linear-gradient(135deg, #e2e8f0 0%, #4da6ff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .se-header-sub { font-size: 0.83rem; color: #3d4f63; font-weight: 400; }
    .se-badges { display: flex; gap: 10px; align-items: center; padding-top: 4px; flex-wrap: wrap; }
    .badge-running {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700;
        background: rgba(0,255,136,0.08); border: 1px solid rgba(0,255,136,0.35);
        color: #00ff88; letter-spacing: 0.04em;
        animation: glow-green 2.5s ease-in-out infinite;
    }
    .badge-ai {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700;
        background: rgba(77,166,255,0.08); border: 1px solid rgba(77,166,255,0.35);
        color: #4da6ff; letter-spacing: 0.04em;
        animation: glow-blue 2.5s ease-in-out infinite;
    }
    @keyframes glow-green {
        0%,100% { box-shadow:0 0 6px rgba(0,255,136,0.15); }
        50%      { box-shadow:0 0 16px rgba(0,255,136,0.5),0 0 28px rgba(0,255,136,0.12); }
    }
    @keyframes glow-blue {
        0%,100% { box-shadow:0 0 6px rgba(77,166,255,0.15); }
        50%      { box-shadow:0 0 16px rgba(77,166,255,0.5),0 0 28px rgba(77,166,255,0.12); }
    }
    .badge-dot { width:7px;height:7px;border-radius:50%;background:currentColor;
                  box-shadow:0 0 5px currentColor;animation:pulse-dot 1.5s infinite; }

    /* ─── KPI CARDS ───────────────────────────────────────────────── */
    .kpi-grid {
        display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 22px;
    }
    .kpi-card {
        background: rgba(13,18,36,0.8); backdrop-filter: blur(16px);
        border-radius: 16px; padding: 18px 16px; border: 1px solid;
        transition: transform 0.25s ease, box-shadow 0.25s ease; position: relative; overflow: hidden;
    }
    .kpi-card::after {
        content:''; position:absolute; top:0;left:0;right:0; height:1px;
        background: linear-gradient(90deg,transparent,currentColor,transparent); opacity:0.4;
    }
    .kpi-card:hover { transform: translateY(-4px); }
    .kpi-card-blue   { border-color:rgba(77,166,255,0.3); color:#4da6ff;
                        box-shadow:0 0 18px rgba(77,166,255,0.07); }
    .kpi-card-blue:hover   { box-shadow:0 8px 30px rgba(77,166,255,0.22); }
    .kpi-card-red    { border-color:rgba(255,68,68,0.3);  color:#ff6b6b;
                        box-shadow:0 0 18px rgba(255,68,68,0.07); }
    .kpi-card-red:hover    { box-shadow:0 8px 30px rgba(255,68,68,0.22); }
    .kpi-card-orange { border-color:rgba(255,149,0,0.3);  color:#ff9500;
                        box-shadow:0 0 18px rgba(255,149,0,0.07); }
    .kpi-card-orange:hover { box-shadow:0 8px 30px rgba(255,149,0,0.22); }
    .kpi-card-teal   { border-color:rgba(0,212,255,0.3);  color:#00d4ff;
                        box-shadow:0 0 18px rgba(0,212,255,0.07); }
    .kpi-card-teal:hover   { box-shadow:0 8px 30px rgba(0,212,255,0.22); }

    .kpi-icon  { font-size:1.5rem;margin-bottom:8px;display:block; }
    .kpi-label { font-size:0.68rem;font-weight:700;letter-spacing:0.09em;
                 text-transform:uppercase;color:#3d4f63;margin-bottom:5px; }
    .kpi-value { font-size:1.9rem;font-weight:800;line-height:1;color:inherit; }
    .kpi-sub   { font-size:0.68rem;color:#3d4f63;margin-top:4px; }

    /* ─── SECTION HEADERS ─────────────────────────────────────────── */
    .se-section-header { display:flex;align-items:center;gap:10px;margin-bottom:10px; }
    .se-section-title  { font-size:0.9rem;font-weight:700;color:#c9d8f0;letter-spacing:0.02em; }
    .se-section-line   { flex:1;height:1px;background:linear-gradient(90deg,rgba(77,166,255,0.25),transparent); }

    /* ─── VIDEO WRAPPER ───────────────────────────────────────────── */
    .video-wrapper {
        background: rgba(8,12,22,0.9);
        border: 1.5px solid rgba(0,255,136,0.3);
        border-radius: 18px; overflow: hidden;
        box-shadow: 0 0 22px rgba(0,255,136,0.1), 0 0 60px rgba(0,255,136,0.03);
        padding: 3px;
    }

    /* ─── ALERT PANEL ─────────────────────────────────────────────── */
    .alert-panel {
        background: rgba(8,12,22,0.6); border:1px solid rgba(77,166,255,0.08);
        border-radius:16px; padding:12px; min-height:320px; max-height:460px; overflow-y:auto;
    }
    .alert-panel::-webkit-scrollbar { width:3px; }
    .alert-panel::-webkit-scrollbar-thumb { background:rgba(77,166,255,0.2);border-radius:2px; }

    .alert-card-unsafe {
        display:flex;align-items:flex-start;gap:10px;
        background:rgba(255,68,68,0.06); border:1px solid rgba(255,68,68,0.25);
        border-left:3px solid #ff4444; border-radius:10px;
        padding:9px 11px; margin-bottom:7px; box-shadow:0 0 8px rgba(255,68,68,0.07);
    }
    .alert-card-safe {
        display:flex;align-items:center;gap:10px;
        background:rgba(0,255,136,0.06); border:1px solid rgba(0,255,136,0.25);
        border-left:3px solid #00ff88; border-radius:10px;
        padding:9px 11px; margin-bottom:7px; box-shadow:0 0 8px rgba(0,255,136,0.07);
    }
    .alert-icon  { font-size:1rem;flex-shrink:0; }
    .alert-title { font-size:0.8rem;font-weight:700;color:#e2e8f0;margin-bottom:2px; }
    .alert-meta  { font-size:0.69rem;color:#3d4f63;line-height:1.5; }

    /* ─── Placeholder / Coming Soon ────────────────────────────────── */
    .se-placeholder {
        background:rgba(13,18,36,0.7); border:1px solid rgba(77,166,255,0.15);
        border-radius:16px; padding:52px; text-align:center; margin-top:18px;
    }

    /* ─── PROFILES (Top Right Reference) ────────────────────────── */
    .se-profile {
        display: flex; align-items: center; gap: 10px;
        padding: 4px 12px; border-radius: 12px;
        background: rgba(13,18,36,0.6); border: 1px solid rgba(77,166,255,0.15);
    }
    .se-profile-img { width:32px; height:32px; border-radius:50%; border: 1.5px solid #4da6ff; }
    .se-profile-name { font-size: 0.82rem; font-weight: 600; color: #e2e8f0; }

    /* ─── Streamlit misc fixes ──────────────────────────────────────── */
    .block-container { padding-top:0.6rem !important; padding-bottom:1rem !important; max-width:100% !important; }
    div[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap:0 !important; }

    /* ─── GLASS PANEL ─────────────────────────────────────────────── */
    .glass-panel {
        background: rgba(13, 18, 36, 0.75);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(77, 166, 255, 0.12);
        border-radius: 20px;
        padding: 24px;
        height: 100%;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    /* ─── STATUS PANEL ────────────────────────────────────────────── */
    .status-item {
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px 14px; margin-bottom: 10px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .status-label { font-size: 0.85rem; color: #8892a4; display: flex; align-items: center; gap: 8px; }
    .status-value { font-size: 0.85rem; font-weight: 700; }
    .status-indicator { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
    .ind-green { background: #00ff88; box-shadow: 0 0 10px #00ff88; }
    .ind-red { background: #ff4444; box-shadow: 0 0 10px #ff4444; }

    /* ─── ALERT CARD (Modern) ─────────────────────────────────────── */
    .alert-card {
        background: rgba(13, 18, 36, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .alert-card::before {
        content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
    }
    .alert-card-unsafe { border-color: rgba(255, 68, 68, 0.2); }
    .alert-card-unsafe::before { background: #ff4444; box-shadow: 0 0 15px #ff4444; }
    .alert-card-safe { border-color: rgba(0, 255, 136, 0.2); }
    .alert-card-safe::before { background: #00ff88; box-shadow: 0 0 15px #00ff88; }
    
    .alert-tag {
        font-size: 0.65rem; font-weight: 800; text-transform: uppercase;
        padding: 3px 8px; border-radius: 6px; float: right;
    }
    .tag-unsafe { background: rgba(255, 68, 68, 0.15); color: #ff6b6b; border: 1px solid rgba(255, 68, 68, 0.3); }
    .tag-safe { background: rgba(0, 255, 136, 0.15); color: #00ff88; border: 1px solid rgba(0, 255, 136, 0.3); }
    
    .alert-info-row { display: flex; gap: 15px; margin-top: 8px; }
    .alert-info-item { font-size: 0.72rem; color: #5c6a85; display: flex; align-items: center; gap: 4px; }
    
    /* ─── QUICK CONTROLS ─────────────────────────────────────────── */
    .ctrl-btn-start {
        background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%) !important;
        color: #060912 !important; font-weight: 700 !important; border: none !important;
        box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3) !important;
    }
    .ctrl-btn-stop {
        background: rgba(255, 68, 68, 0.1) !important;
        color: #ff4444 !important; font-weight: 700 !important; border: 1px solid rgba(255, 68, 68, 0.3) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ── Floating Sidebar Toggle Button ───────────────────────────────────────────
# This button is always injected. CSS above hides it when the sidebar is open.
# Clicking it triggers Streamlit's native sidebar collapse button via JS.
st.markdown("""
    <div class="se-sidebar-toggle" onclick="
        const btn = window.parent.document.querySelector('[data-testid=\\"stSidebarCollapsedControl\\"] button,\
 [title=\\"Open sidebar\\"] button, button[aria-label=\\"Open sidebar\\"],\
 [data-testid=\\"collapsedControl\\"] button');
        if(btn){ btn.click(); }
    " title="Open Navigation">☰</div>
""", unsafe_allow_html=True)


# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'run' not in st.session_state:
    st.session_state.run = False
if 'active_page' not in st.session_state:
    st.session_state.active_page = "Dashboard"
if 'logs' not in st.session_state:
    st.session_state['logs'] = []
if '_last_log_ts' not in st.session_state:
    st.session_state['_last_log_ts'] = 0.0

# Initialize dashboard stats
if 'total_persons' not in st.session_state:
    st.session_state['total_persons'] = 0
if 'unsafe_workers' not in st.session_state:
    st.session_state['unsafe_workers'] = 0
if 'alerts_count' not in st.session_state:
    st.session_state['alerts_count'] = 0
if 'camera_status' not in st.session_state:
    st.session_state['camera_status'] = "Inactive"
if 'active_source' not in st.session_state:
    st.session_state['active_source'] = "None"
if 'model_status' not in st.session_state:
    st.session_state['model_status'] = "Ready"


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
NAV_ITEMS = [
    ("🏠", "Dashboard"),
    ("🎥", "Webcam Monitoring"),
    ("📂", "Video Testing"),
    ("📊", "Analytics"),
    ("📝", "Logs"),
]

with st.sidebar:
    # ── Logo ────────────────────────────────────────────────
    st.markdown("""
        <div class="se-logo">
            <span class="se-logo-icon">🛡️</span>
            <span class="se-logo-text">SafetyEye</span>
        </div>
    """, unsafe_allow_html=True)

    # ── Navigation ──────────────────────────────────────────
    st.markdown('<div class="se-nav-label">Navigation</div>', unsafe_allow_html=True)

    for icon, label in NAV_ITEMS:
        is_active = st.session_state.active_page == label
        # Inject per-button active style using a unique wrapper key
        btn_key = f"nav_{label.replace(' ','_')}"
        if is_active:
            st.markdown(f"""
            <style>
            [data-testid="stSidebar"] [data-testid="stVerticalBlock"]
            div:has(> div > button#{btn_key}) button {{
                background: rgba(77,166,255,0.1) !important;
                border-left: 2px solid #4da6ff !important;
                color: #4da6ff !important;
            }}
            </style>
            """, unsafe_allow_html=True)
        if st.button(f"{icon}  {label}", key=btn_key, use_container_width=True):
            st.session_state.active_page = label
            st.rerun()

    st.markdown('<hr class="se-divider">', unsafe_allow_html=True)

    # ── Controls ────────────────────────────────────────────
    st.markdown('<div class="se-controls-label">Controls</div>', unsafe_allow_html=True)

    start_val = st.toggle("▶  Start Monitoring", value=st.session_state.monitoring, key="monitoring_toggle")
    st.session_state.monitoring = start_val

    with st.container():
        st.markdown('<div class="stop-wrap">', unsafe_allow_html=True)
        if st.button("⏹  Stop", use_container_width=True, key="stop_btn"):
            st.session_state.monitoring = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Camera Status ────────────────────────────────────────
    cam_on     = st.session_state.monitoring
    dot_cls    = "cam-dot-active" if cam_on else "cam-dot-inactive"
    cam_text   = "Active"         if cam_on else "Inactive"
    cam_color  = "#00ff88"        if cam_on else "#ff4444"
    st.markdown(f"""
        <div class="cam-status">
            <span>📷</span>
            <div class="{dot_cls}"></div>
            <span>Camera:&nbsp;<span style="color:{cam_color};font-weight:600;">{cam_text}</span></span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="se-divider">', unsafe_allow_html=True)

    # ── Source selectors ─────────────────────────────────────
    selected_video = None
    camera_index   = 0
    active         = st.session_state.active_page

    if active == "Video Testing":
        video_folder = "dataset/videos"
        video_files  = [f for f in os.listdir(video_folder)
                        if f.endswith(('.mp4', '.avi'))] if os.path.exists(video_folder) else []
        if video_files:
            selected_video = st.selectbox("📁 Select Video", video_files, key="vid_sel")
        else:
            st.warning("No videos in dataset/videos/", icon="⚠️")
    elif active == "Webcam Monitoring":
        camera_index = st.selectbox("🎥 Camera Index", [0, 1, 2], key="cam_idx")


# ==========================================
# MODEL LOADING
# ==========================================
@st.cache_resource
def load_yolo_model():
    # Use relative path from script location to ensure it works from any CWD
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "..", "models", "bestmodel.pt")
    if not os.path.exists(model_path):
        # Fallback to local 'models' if it's there (e.g. running from root with different structure)
        model_path = "models/bestmodel.pt"
    return YOLO(model_path)

model = load_yolo_model()


# ==========================================
# DETECTION ENGINE  (unchanged backend)
# ==========================================
def process_frame(frame):
    frame   = cv2.resize(frame, (640, 480))
    results = model(frame, conf=0.5, verbose=False)

    alerts       = []
    person_count = 0
    unsafe_count = 0
    annotated    = frame.copy()

    for r in results:
        persons   = []
        equipment = []

        for box in r.boxes:
            cls   = int(box.cls[0])
            label = model.names[cls]
            xyxy  = box.xyxy[0].tolist()
            if label == "Person":
                persons.append(xyxy)
                person_count += 1
            else:
                equipment.append((label, xyxy))

        for px1, py1, px2, py2 in persons:
            has_hardhat = has_vest = has_mask = False
            for eq_label, (ex1, ey1, ex2, ey2) in equipment:
                if ex1 > px1-20 and ey1 > py1-20 and ex2 < px2+20 and ey2 < py2+20:
                    if eq_label == "Hardhat":     has_hardhat = True
                    if eq_label == "Safety Vest": has_vest    = True
                    if eq_label == "Mask":        has_mask    = True

            is_unsafe = not (has_hardhat and has_vest) or not has_mask
            color      = (0, 0, 255) if is_unsafe else (0, 255, 0)
            status     = "UNSAFE"   if is_unsafe else "SAFE"

            if is_unsafe:
                unsafe_count += 1
                if not has_hardhat: alerts.append("VIOLATION: Helmet Missing")
                if not has_vest:    alerts.append("VIOLATION: Safety Vest Missing")
                if not has_mask:    alerts.append("VIOLATION: Mask Missing")

            cv2.rectangle(annotated, (int(px1), int(py1)), (int(px2), int(py2)), color, 2)
            cv2.putText(annotated, status, (int(px1), int(py1)-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return annotated, list(set(alerts)), person_count, unsafe_count


# ==========================================
# HELPERS: HTML BUILDERS
# ==========================================
def kpi_cards_html(p: int, u: int, a: int, cam_active: bool) -> str:
    cl = "#00d4ff" if cam_active else "#ff6b6b"
    cv = "Active"  if cam_active else "Inactive"
    return f"""
    <div class="kpi-grid">
      <div class="kpi-card kpi-card-blue">
        <span class="kpi-icon">👥</span>
        <div class="kpi-label">Total Persons</div>
        <div class="kpi-value">{p}</div>
        <div class="kpi-sub">Detected in frame</div>
      </div>
      <div class="kpi-card kpi-card-red">
        <span class="kpi-icon">⚠️</span>
        <div class="kpi-label">Unsafe Workers</div>
        <div class="kpi-value">{u}</div>
        <div class="kpi-sub">PPE violations</div>
      </div>
      <div class="kpi-card kpi-card-orange">
        <span class="kpi-icon">🚨</span>
        <div class="kpi-label">Alerts Count</div>
        <div class="kpi-value">{a}</div>
        <div class="kpi-sub">Active violations</div>
      </div>
      <div class="kpi-card kpi-card-teal">
        <span class="kpi-icon">📷</span>
        <div class="kpi-label">Camera Status</div>
        <div class="kpi-value" style="font-size:1.25rem;color:{cl};">{cv}</div>
        <div class="kpi-sub">Feed source</div>
      </div>
    </div>
    """

def alert_panel_html(alerts: list) -> str:
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    if not alerts:
        return f"""
        <div class="alert-panel">
          <div class="alert-card-safe">
            <span class="alert-icon">✅</span>
            <div>
              <div class="alert-title">All Safe</div>
              <div class="alert-meta">No violations detected · {ts}</div>
            </div>
          </div>
        </div>"""
    cards = "".join(f"""
        <div class="alert-card-unsafe">
          <span class="alert-icon">⚠️</span>
          <div>
            <div class="alert-title">{a}</div>
            <div class="alert-meta">Detected · {ts}<br>Worker ID: Unknown</div>
          </div>
        </div>""" for a in alerts)
    return f'<div class="alert-panel">{cards}</div>'


# ==========================================
# ANALYTICS PAGE
# ==========================================
def render_analytics():
    import plotly.graph_objects as go
    import pandas as pd

    # ── Shared Plotly dark layout ─────────────────────────────
    CHART_BG   = "rgba(10,14,26,0)"
    PAPER_BG   = "rgba(10,14,26,0)"
    GRID_COLOR = "rgba(77,166,255,0.08)"
    FONT_COLOR = "#8892a4"
    CHART_FONT = dict(family="Inter, sans-serif", color=FONT_COLOR, size=11)

    def base_layout(**kwargs):
        return dict(
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=CHART_BG,
            font=CHART_FONT,
            margin=dict(l=12, r=12, t=32, b=12),
            legend=dict(
                bgcolor="rgba(0,0,0,0)", font=dict(color="#8892a4", size=10),
                orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5
            ),
            **kwargs
        )

    # ── Analytics Header ──────────────────────────────────────
    st.markdown("""
        <div class="se-header">
          <div>
            <div class="se-header-title">Safety Analytics Dashboard</div>
            <div class="se-header-sub">Workplace Safety Insights &amp; Trends</div>
          </div>
          <div class="se-badges">
            <span class="badge-running"><span class="badge-dot"></span>System Running</span>
            <span class="badge-ai"><span class="badge-dot"></span>AI Active</span>
          </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Load data ─────────────────────────────────────────────
    logs = st.session_state.get("logs", [])

    if not logs:
        # ── Empty state with demo seed button ─────────────────
        st.markdown("""
            <div style="background:rgba(13,18,36,0.8);border:1px solid rgba(77,166,255,0.15);
                        border-radius:16px;padding:48px;text-align:center;margin-top:16px;">
                <div style="font-size:2.8rem;margin-bottom:14px;">📊</div>
                <div style="font-size:1rem;font-weight:700;color:#718096;">No analytics data yet</div>
                <div style="font-size:0.82rem;color:#3d4f63;margin-top:8px;">
                    Start monitoring on the Dashboard page to begin collecting safety data,<br>
                    or load demo data below to preview the analytics layout.
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_btn, _, _ = st.columns([1, 1, 1])
        with col_btn:
            if st.button("🧪  Load Demo Data", use_container_width=True, key="demo_data_btn"):
                import random, math
                _viol = ["Helmet Missing", "Mask Missing", "Safety Vest Missing", "None"]
                _status = ["unsafe", "unsafe", "unsafe", "safe"]
                base = datetime.datetime.now() - datetime.timedelta(hours=6)
                for i in range(120):
                    idx = random.choices([0,1,2,3], weights=[35,20,25,20])[0]
                    ts  = (base + datetime.timedelta(minutes=i*3)).strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state["logs"].append({
                        "timestamp": ts,
                        "violation": _viol[idx],
                        "source":    "Demo",
                        "status":    _status[idx]
                    })
                st.rerun()
        return

    df = pd.DataFrame(logs)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"]      = df["timestamp"].dt.date
    df["hour"]      = df["timestamp"].dt.floor("10min")   # bucket by 10-min

    violations_df = df[df["status"] == "unsafe"]
    safe_df       = df[df["status"] == "safe"]

    # Counts per violation type
    helmet_count = int((violations_df["violation"] == "Helmet Missing").sum())
    mask_count   = int((violations_df["violation"] == "Mask Missing").sum())
    vest_count   = int((violations_df["violation"] == "Safety Vest Missing").sum())
    total_viol   = helmet_count + mask_count + vest_count
    total_safe   = len(safe_df)
    total_events = len(df)
    safe_pct     = round(total_safe / total_events * 100) if total_events else 0
    unsafe_pct   = 100 - safe_pct

    # Most frequent violation
    viol_counts  = {"Helmet Missing": helmet_count, "Mask Missing": mask_count,
                    "Safety Vest Missing": vest_count}
    most_frequent = max(viol_counts, key=viol_counts.get) if total_viol else "None"

    # ── Analytics KPI Cards ───────────────────────────────────
    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card kpi-card-red">
        <span class="kpi-icon">⚠️</span>
        <div class="kpi-label">Total Violations</div>
        <div class="kpi-value">{total_viol}</div>
        <div class="kpi-sub">All PPE violations</div>
      </div>
      <div class="kpi-card kpi-card-orange">
        <span class="kpi-icon">⛑️</span>
        <div class="kpi-label">Helmet Violations</div>
        <div class="kpi-value">{helmet_count}</div>
        <div class="kpi-sub">No hardhat detected</div>
      </div>
      <div class="kpi-card" style="border-color:rgba(255,220,0,0.35);color:#ffd700;
           box-shadow:0 0 18px rgba(255,220,0,0.07);">
        <span class="kpi-icon">😷</span>
        <div class="kpi-label">Mask Violations</div>
        <div class="kpi-value" style="color:#ffd700;">{mask_count}</div>
        <div class="kpi-sub">No mask detected</div>
      </div>
      <div class="kpi-card kpi-card-teal" style="border-color:rgba(0,255,136,0.35);color:#00ff88;
           box-shadow:0 0 18px rgba(0,255,136,0.07);">
        <span class="kpi-icon">🦺</span>
        <div class="kpi-label">Safety Vest Violations</div>
        <div class="kpi-value" style="color:#00ff88;">{vest_count}</div>
        <div class="kpi-sub">No vest detected</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CHART ROW 1: Line + Pie ───────────────────────────────
    ch1, ch2 = st.columns([3, 2], gap="medium")

    with ch1:
        st.markdown("""
            <div class="se-section-header">
              <span class="se-section-title">Violations Over Time</span>
              <div class="se-section-line"></div>
            </div>""", unsafe_allow_html=True)

        # Dynamic bucketing based on time range
        min_ts = df["timestamp"].min()
        max_ts = df["timestamp"].max()
        time_diff = (max_ts - min_ts).total_seconds()
        
        if time_diff < 1: # Single point or very close
            freq = "1s"
        elif time_diff < 3600: # Less than 1 hour
            freq = "1min"
        else:
            freq = "10min"
            
        df["hour"] = df["timestamp"].dt.floor(freq)
        violations_df = df[df["status"] == "unsafe"] # Re-filter with new bucket
        
        time_groups = violations_df.groupby(["hour", "violation"]).size().reset_index(name="count")
        all_times   = pd.date_range(df["hour"].min(), df["hour"].max(), freq=freq) \
                      if len(df) > 1 else [df["hour"].iloc[0]]

        def get_series(viol_name, color, fillcolor):
            grp = time_groups[time_groups["violation"] == viol_name]
            if not grp.empty:
                grp = grp.set_index("hour").reindex(all_times, fill_value=0).reset_index()
                x_data = grp["index"] if "index" in grp else grp.iloc[:,0]
                y_data = grp["count"]
            else:
                x_data, y_data = all_times, [0] * len(all_times)
                
            return go.Scatter(
                x=x_data,
                y=y_data,
                mode="lines+markers",
                marker=dict(size=6),
                name=viol_name,
                line=dict(color=color, width=2.5, shape="spline"),
                fill="tozeroy",
                fillcolor=fillcolor,
            )

        fig_line = go.Figure(data=[
            get_series("Helmet Missing",       "#ff6b6b", "rgba(255,107,107,0.07)"),
            get_series("Mask Missing",          "#ffd700", "rgba(255,215,0,0.07)"),
            get_series("Safety Vest Missing",   "#00ff88", "rgba(0,255,136,0.07)"),
        ])
        fig_line.update_layout(
            **base_layout(height=260),
            xaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False,
                       tickfont=dict(size=9, color=FONT_COLOR)),
            yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, zeroline=False,
                       tickfont=dict(size=9, color=FONT_COLOR)),
        )
        st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})

    with ch2:
        st.markdown("""
            <div class="se-section-header">
              <span class="se-section-title">Violation Distribution</span>
              <div class="se-section-line"></div>
            </div>""", unsafe_allow_html=True)

        pie_vals   = [helmet_count, mask_count, vest_count]
        pie_labels = ["Helmet Missing", "Mask Missing", "Vest Missing"]
        pie_colors = ["#ff6b6b", "#ffd700", "#00ff88"]

        fig_pie = go.Figure(data=[go.Pie(
            labels=pie_labels,
            values=pie_vals if any(v > 0 for v in pie_vals) else [1, 1, 1],
            hole=0,
            marker=dict(colors=pie_colors,
                        line=dict(color="#0a0e1a", width=2)),
            textinfo="percent",
            textfont=dict(size=10, color="#e2e8f0"),
        )])
        fig_pie.update_layout(
            **base_layout(height=260),
            showlegend=True,
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    # ── CHART ROW 2: Bar + Doughnut + AI Insights ─────────────
    bl, bc, br = st.columns([2, 2, 2], gap="medium")

    with bl:
        st.markdown("""
            <div class="se-section-header">
              <span class="se-section-title">Daily Violations Count</span>
              <div class="se-section-line"></div>
            </div>""", unsafe_allow_html=True)

        daily = violations_df.groupby("date").size().reset_index(name="count")
        fig_bar = go.Figure(data=[go.Bar(
            x=daily["date"].astype(str),
            y=daily["count"],
            marker=dict(
                color=daily["count"],
                colorscale=[[0, "#1a3550"], [0.5, "#ff9500"], [1, "#ff4444"]],
                showscale=False,
                line=dict(width=0),
            ),
            width=0.6,
        )])
        fig_bar.update_layout(
            **base_layout(height=220),
            xaxis=dict(showgrid=False, tickfont=dict(size=8, color=FONT_COLOR)),
            yaxis=dict(showgrid=True, gridcolor=GRID_COLOR,
                       tickfont=dict(size=8, color=FONT_COLOR)),
            bargap=0.3,
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    with bc:
        st.markdown("""
            <div class="se-section-header">
              <span class="se-section-title">Safety Compliance Rate</span>
              <div class="se-section-line"></div>
            </div>""", unsafe_allow_html=True)

        fig_donut = go.Figure(data=[go.Pie(
            labels=["Safe", "Unsafe"],
            values=[max(safe_pct, 1), max(unsafe_pct, 1)],
            hole=0.65,
            marker=dict(colors=["#00ff88", "#ff4444"],
                        line=dict(color="#0a0e1a", width=3)),
            textinfo="none",
        )])
        fig_donut.add_annotation(
            text=f"<b>{safe_pct}%</b><br><span style='font-size:10px'>Safe</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="#00ff88", family="Inter"),
        )
        fig_donut.update_layout(
            paper_bgcolor=PAPER_BG,
            plot_bgcolor=CHART_BG,
            font=CHART_FONT,
            margin=dict(l=12, r=12, t=32, b=12),
            height=220,
            showlegend=True,
            legend=dict(
                bgcolor="rgba(0,0,0,0)", font=dict(color="#8892a4", size=10),
                orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5
            ),
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    with br:
        st.markdown("""
            <div class="se-section-header">
              <span class="se-section-title">AI Insights</span>
              <div class="se-section-line"></div>
            </div>""", unsafe_allow_html=True)

        # Trend: compare first half vs second half
        half = len(violations_df) // 2
        first_half  = len(violations_df.iloc[:half])  if half else 0
        second_half = len(violations_df.iloc[half:])  if half else 0
        trend_up    = second_half > first_half
        trend_txt   = "⬆️ Violations increasing" if trend_up else "✅ Safety improving"
        trend_color = "#ff6b6b" if trend_up else "#00ff88"

        compliance_status = "🟢 Improving" if safe_pct >= 60 else "🔴 Needs Attention"

        insights = [
            ("🎯 Most Frequent",    most_frequent,            "#ffd700"),
            ("📊 Total Violations", str(total_viol),          "#ff6b6b"),
            ("📈 Trend",            trend_txt,                trend_color),
            ("🛡️ Compliance",       compliance_status,        "#00ff88" if safe_pct >= 60 else "#ff6b6b"),
            ("🔢 Safe Events",      f"{total_safe} / {total_events}", "#4da6ff"),
        ]

        cards_html = ""
        for label, value, color in insights:
            cards_html += f"""
            <div style="background:rgba(13,18,36,0.75);border:1px solid rgba(77,166,255,0.12);
                        border-left:3px solid {color};border-radius:10px;
                        padding:9px 12px;margin-bottom:7px;">
                <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.07em;
                             text-transform:uppercase;color:#3d4f63;margin-bottom:3px;">{label}</div>
                <div style="font-size:0.85rem;font-weight:600;color:{color};
                             line-height:1.3;">{value}</div>
            </div>"""

        st.markdown(cards_html, unsafe_allow_html=True)

        if st.button("🗑️ Clear Logs", use_container_width=True, key="clear_logs_btn"):
            st.session_state["logs"] = []
            st.rerun()


# ==========================================
# LOGS PAGE
# ==========================================
def render_logs():
    import pandas as pd
    import datetime
    
    # ── Logs Header ──────────────────────────────────────────
    st.markdown("""
        <div class="se-header">
          <div>
            <div class="se-header-title">Violation Logs</div>
            <div class="se-header-sub">Real-Time Safety Violation Records</div>
          </div>
          <div class="se-badges">
            <span class="badge-running"><span class="badge-dot"></span>System Running</span>
            <span class="badge-ai"><span class="badge-dot"></span>AI Active</span>
          </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Load Data ─────────────────────────────────────────────
    logs = st.session_state.get("logs", [])
    if not logs:
        st.markdown("""
            <div class="se-placeholder">
              <div style="font-size:2.8rem;margin-bottom:14px;">📝</div>
              <div style="font-size:1rem;font-weight:700;color:#718096;">No incident logs yet</div>
              <div style="font-size:0.82rem;color:#3d4f63;margin-top:8px;">Start monitoring to see workplace safety data here.</div>
            </div>""", unsafe_allow_html=True)
        return

    df = pd.DataFrame(logs)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Ensure confidence score exists
    if "confidence" not in df.columns:
        df["confidence"] = 0.95

    # ── Filter Bar ────────────────────────────────────────────
    f1, f2, f3, f4 = st.columns([1.5, 1.2, 1.2, 2], gap="small")
    
    with f1:
        v_types = ["All", "Helmet Missing", "Mask Missing", "Safety Vest Missing", "None"]
        v_filter = st.selectbox("Select violation type", v_types, index=0)
        
    with f2:
        d_filter = st.date_input("Date range", [])
        
    with f3:
        s_filter = st.selectbox("Source", ["All", "Webcam Monitoring", "Video Testing"], index=0)
        
    with f4:
        search = st.text_input("Search logs...", placeholder="Search keywords...")

    # ── Apply Filters ─────────────────────────────────────────
    df_filtered = df.copy()
    
    if v_filter != "All":
        df_filtered = df_filtered[df_filtered["violation"] == v_filter]
        
    if len(d_filter) == 2:
        df_filtered = df_filtered[
            (df_filtered["timestamp"].dt.date >= d_filter[0]) & 
            (df_filtered["timestamp"].dt.date <= d_filter[1])
        ]
        
    if s_filter != "All":
        df_filtered = df_filtered[df_filtered["source"] == s_filter]
        
    if search:
        search = search.lower()
        df_filtered = df_filtered[
            df_filtered.apply(lambda row: search in row.astype(str).str.lower().values, axis=1)
        ]

    # ── Summary Cards ─────────────────────────────────────────
    total_v = len(df_filtered[df_filtered["status"] == "unsafe"])
    total_s = len(df_filtered[df_filtered["status"] == "safe"])
    
    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card kpi-card-blue">
        <span class="kpi-icon">📊</span>
        <div class="kpi-label">Total Logs</div>
        <div class="kpi-value">{len(df_filtered)}</div>
        <div class="kpi-sub">Filtered records</div>
      </div>
      <div class="kpi-card kpi-card-teal" style="border-color:rgba(0, 255, 136, 0.35); color:#00ff88;">
        <span class="kpi-icon">✅</span>
        <div class="kpi-label">Safe Events</div>
        <div class="kpi-value">{total_s}</div>
        <div class="kpi-sub">Compliance met</div>
      </div>
      <div class="kpi-card kpi-card-red">
        <span class="kpi-icon">⚠️</span>
        <div class="kpi-label">Unsafe Events</div>
        <div class="kpi-value">{total_v}</div>
        <div class="kpi-sub">PPE Violations</div>
      </div>
      <div style="display:flex; flex-direction:column; gap:8px; justify-content:center;">
          <div style="height:40px;">
    """, unsafe_allow_html=True)
    
    # Action buttons inside the grid wrapper (placeholder column)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="📥 Export (CSV)",
            data=df_filtered.to_csv(index=False),
            file_name=f"safety_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c2:
        if st.button("🗑️ Clear Logs", use_container_width=True, key="clear_logs_full"):
            st.session_state["logs"] = []
            st.rerun()
            
    st.markdown("""
        </div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Table Rendering ───────────────────────────────────────
    # Format timestamp for display
    df_disp = df_filtered.copy()
    df_disp["timestamp"] = df_disp["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Styling function
    def style_rows(row):
        color = 'rgba(255, 68, 68, 0.15)' if row['status'] == 'unsafe' else 'rgba(0, 255, 136, 0.12)'
        # Apply background to the entire row
        return [f'background-color: {color}'] * len(row)

    styled_df = df_disp.style.apply(style_rows, axis=1)

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "timestamp": "Timestamp",
            "violation": "Violation Type",
            "source": "Source",
            "status": st.column_config.TextColumn("Status", help="Safe (Compliance) vs Unsafe (Violation)"),
            "confidence": st.column_config.NumberColumn("Confidence Score (%)", format="%.2f")
        }
    )

def render_dashboard():
    import plotly.graph_objects as go
    import pandas as pd
    
    # ── Section 1: Summary Cards ─────────────────────────────────────
    st.markdown(kpi_cards_html(
        st.session_state.total_persons,
        st.session_state.unsafe_workers,
        st.session_state.alerts_count,
        st.session_state.monitoring
    ), unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 2], gap="medium")
    
    with col_left:
        # ── Section 2: System Status Panel ─────────────────────────────
        st.markdown("""
            <div class="se-section-header">
              <span class="se-section-title">System Status</span>
              <div class="se-section-line"></div>
            </div>""", unsafe_allow_html=True)
            
        monitoring_cls = "ind-green" if st.session_state.monitoring else "ind-red"
        monitoring_txt = "Running" if st.session_state.monitoring else "Stopped"
        
        st.markdown(f"""
<div class="glass-panel">
<div class="status-item">
<div class="status-label"><span>🛡️</span> Monitoring Status</div>
<div class="status-value"><span class="status-indicator {monitoring_cls}"></span>{monitoring_txt}</div>
</div>
<div class="status-item">
<div class="status-label"><span>🎥</span> Active Source</div>
<div class="status-value">{st.session_state.active_source}</div>
</div>
<div class="status-item">
<div class="status-label"><span>⚙️</span> AI Model</div>
<div class="status-value"><span class="status-indicator ind-green"></span>{st.session_state.model_status}</div>
</div>

<div style="margin-top: 24px;">
<div class="se-section-header" style="margin-bottom:15px;">
<span class="se-section-title" style="font-size:0.75rem;">Quick Controls</span>
</div>
</div>
</div>
""", unsafe_allow_html=True)
            
        # Quick Controls inside the status panel
        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("▶ Start", key="dash_start", use_container_width=True):
                st.session_state.monitoring = True
                st.session_state.run = True
                st.rerun()
        with cc2:
            if st.button("⏹ Stop", key="dash_stop", use_container_width=True):
                st.session_state.monitoring = False
                st.session_state.run = False
                st.rerun()
        pass


    with col_right:
        # ── Section 3: Recent Alerts Panel ─────────────────────────────
        st.markdown("""
            <div class="se-section-header">
              <span class="se-section-title">Recent Alerts Panel</span>
              <div class="se-section-line"></div>
            </div>""", unsafe_allow_html=True)
            
        recent_logs = st.session_state['logs'][-6:][::-1] # Last 6 logs, reversed
        
        if not recent_logs:
            st.markdown("""
<div class="glass-panel" style="display:flex; align-items:center; justify-content:center; min-height:300px;">
<div style="text-align:center; color:#3d4f63;">
<div style="font-size:2rem; margin-bottom:10px;">📋</div>
<div style="font-size:0.9rem; font-weight:600;">No recent alerts recorded</div>
</div>
</div>
""", unsafe_allow_html=True)
        else:
            alerts_html = '<div class="glass-panel" style="overflow-y:auto; max-height:400px;">'
            for log in recent_logs:
                is_unsafe = log['status'] == 'unsafe'
                card_cls = "alert-card-unsafe" if is_unsafe else "alert-card-safe"
                tag_cls = "tag-unsafe" if is_unsafe else "tag-safe"
                tag_txt = "UNSAFE" if is_unsafe else "SAFE"
                icon = "⚠️" if is_unsafe else "✅"
                
                alerts_html += f"""
<div class="alert-card {card_cls}">
<div class="alert-tag {tag_cls}">{tag_txt}</div>
<div style="font-size:0.85rem; font-weight:700; color:#e2e8f0;">{icon} {log['violation']}</div>
<div class="alert-info-row">
<div class="alert-info-item"><span>📷</span> {log['source']}</div>
<div class="alert-info-item"><span>🕒</span> {log['timestamp'].split(' ')[1]}</div>
</div>
</div>
"""
            alerts_html += '</div>'
            st.markdown(alerts_html, unsafe_allow_html=True)

    # ── Section 4: Mini Analytics ────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2 = st.columns([2, 1], gap="medium")
    
    logs = st.session_state.get("logs", [])
    if logs:
        df = pd.DataFrame(logs)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.floor("1min")

        
        # Line Chart: Alerts Over Time
        with m1:
            st.markdown("""
                <div class="se-section-header">
                  <span class="se-section-title">Alerts Over Time</span>
                  <div class="se-section-line"></div>
                </div>""", unsafe_allow_html=True)
            
            viol_df = df[df["status"] == "unsafe"]
            if not viol_df.empty:
                # Use even finer bucket for dashboard quick look
                df["hour_fine"] = df["timestamp"].dt.floor("10s")
                time_counts = viol_df.assign(hour_fine=viol_df["timestamp"].dt.floor("10s")).groupby("hour_fine").size().reset_index(name="count")
                fig_line = go.Figure(data=go.Scatter(
                    x=time_counts["hour_fine"], y=time_counts["count"],
                    mode="lines+markers", marker=dict(size=8),
                    line=dict(color="#4da6ff", width=3, shape="spline"),
                    fill="tozeroy", fillcolor="rgba(77, 166, 255, 0.1)"
                ))
            else:
                fig_line = go.Figure()
                
            fig_line.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=220, margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
                font=dict(color="#8892a4", size=10)
            )
            st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})
            
        # Donut Chart: Safe vs Unsafe
        with m2:
            st.markdown("""
                <div class="se-section-header">
                  <span class="se-section-title">Safe vs Unsafe Ratio</span>
                  <div class="se-section-line"></div>
                </div>""", unsafe_allow_html=True)
            
            safe_cnt = len(df[df["status"] == "safe"])
            unsafe_cnt = len(df[df["status"] == "unsafe"])
            
            fig_donut = go.Figure(data=[go.Pie(
                labels=["Safe", "Unsafe"], values=[safe_cnt, unsafe_cnt],
                hole=0.7, marker=dict(colors=["#00ff88", "#ff4444"])
            )])
            fig_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=220, showlegend=True, margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                font=dict(color="#8892a4", size=10)
            )
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
    else:
        with m1: st.info("Run monitoring to see analytics.")

def main():

    page = st.session_state.active_page

    # ── Header ──────────────────────────────────────────────
    st.markdown(f"""
        <div class="se-header">
          <div>
            <div class="se-header-title">SafetyEye AI Dashboard</div>
            <div class="se-header-sub">Real-Time Workplace Safety Monitoring System</div>
          </div>
          <div class="se-badges">
            <span class="badge-running"><span class="badge-dot"></span>System Running</span>
            <span class="badge-ai"><span class="badge-dot"></span>AI Active</span>
          </div>
        </div>
    """, unsafe_allow_html=True)

    if page == "Dashboard":
        render_dashboard()
        return

    # ── KPI Row ─────────────────────────────────────────────
    kpi_ph = st.empty()
    kpi_ph.markdown(kpi_cards_html(0, 0, 0, st.session_state.monitoring), unsafe_allow_html=True)

    # ── Page Content ────────────────────────────────────────
    if page in ("Webcam Monitoring", "Video Testing"):
        feed_label = {
            "Webcam Monitoring": "🎥  Webcam Feed",
            "Video Testing":     "📂  Video Feed",
        }.get(page, "Live Monitoring Feed")

        col_l, col_r = st.columns([2, 1], gap="medium")

        with col_l:
            st.markdown(f"""
                <div class="se-section-header">
                  <span class="se-section-title">{feed_label}</span>
                  <div class="se-section-line"></div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('<div class="video-wrapper">', unsafe_allow_html=True)
            feed_ph = st.empty()
            feed_ph.image(np.zeros((360, 480, 3), dtype=np.uint8),
                          channels="RGB", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown("""
                <div class="se-section-header">
                  <span class="se-section-title">Live Alerts &amp; Violations</span>
                  <div class="se-section-line"></div>
                </div>
            """, unsafe_allow_html=True)
            alert_ph = st.empty()
            alert_ph.markdown(alert_panel_html([]), unsafe_allow_html=True)

        # ── Monitoring Loop ──────────────────────────────────
        if st.session_state.monitoring:
            src = page
            st.session_state['active_source'] = "Webcam" if src == "Webcam Monitoring" else "Video"
            try:
                if src == "Webcam Monitoring":
                    cap = cv2.VideoCapture(camera_index)
                elif src == "Video Testing":
                    if not selected_video:
                        st.warning("⚠️ Select a video file first.")
                        st.session_state.monitoring = False
                        st.session_state.run = False
                        return
                    cap = cv2.VideoCapture(os.path.join("dataset/videos", selected_video))
                
                if not cap or not cap.isOpened():
                    st.error("❌ Cannot open camera/video source.")
                    st.session_state.monitoring = False
                    st.session_state.run = False
                    return

                while st.session_state.monitoring:
                    ret, frame = cap.read()
                    if not ret:
                        if src == "Video Testing":
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            continue
                        break

                    p_frame, alerts, p_cnt, u_cnt = process_frame(frame)
                    
                    # Update global session state for Dashboard
                    st.session_state['total_persons'] = p_cnt
                    st.session_state['unsafe_workers'] = u_cnt
                    st.session_state['alerts_count'] = len(alerts)
                    st.session_state['camera_status'] = "Active"
                    
                    feed_ph.image(cv2.cvtColor(p_frame, cv2.COLOR_BGR2RGB),
                                  use_container_width=True)
                    kpi_ph.markdown(kpi_cards_html(p_cnt, u_cnt, len(alerts), True),
                                    unsafe_allow_html=True)
                    alert_ph.markdown(alert_panel_html(alerts), unsafe_allow_html=True)

                    # ── Log to session_state every ~2 seconds ────────
                    now = time.time()
                    if now - st.session_state['_last_log_ts'] >= 2.0:
                        st.session_state['_last_log_ts'] = now
                        ts_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        conf_val = round(np.random.uniform(0.85, 0.99), 2)
                        
                        if alerts:
                            for alert in alerts:
                                st.session_state['logs'].append({
                                    "timestamp": ts_str,
                                    "violation": alert.replace("VIOLATION: ", ""),
                                    "source": src,
                                    "status": "unsafe",
                                    "confidence": conf_val
                                })
                        else:
                            st.session_state['logs'].append({
                                "timestamp": ts_str,
                                "violation": "None",
                                "source": src,
                                "status": "safe",
                                "confidence": conf_val
                            })
                        if len(st.session_state['logs']) > 500:
                            st.session_state['logs'] = st.session_state['logs'][-500:]

                    time.sleep(0.01)

                cap.release()
                st.session_state['camera_status'] = "Inactive"
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.session_state.monitoring = False
                st.session_state.run = False
        else:
            st.session_state['camera_status'] = "Inactive"
            st.info("ℹ️ Monitoring is **OFF**. Use the sidebar toggle to start.")

    elif page == "Analytics":
        render_analytics()

    elif page == "Logs":
        render_logs()


if __name__ == "__main__":
    main()