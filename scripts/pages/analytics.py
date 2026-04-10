import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import datetime
import random
import math

def render_analytics():
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
            # Use original strings to match detections exactly
            grp = time_groups[time_groups["violation"].str.strip() == viol_name.strip()]
            if not grp.empty:
                # Ensure aligning indices by explicitly setting frequency and using the floor-aligned hour
                grp = grp.set_index("hour").reindex(all_times, fill_value=0).reset_index()
                # Clean up the reset index column name (which was 'hour')
                x_data = grp["hour"] if "hour" in grp else grp.iloc[:, 0]
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
        pie_labels = ["Helmet Missing", "Mask Missing", "Safety Vest Missing"]
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
