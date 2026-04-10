import streamlit as st
import pandas as pd
import datetime

def render_logs():
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
