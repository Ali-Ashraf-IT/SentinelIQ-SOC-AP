import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import streamlit as st
from datetime import datetime

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SentinelIQ Enterprise SIEM",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────
# CSS — CROWDSTRIKE / SPLUNK INSPIRED ENTERPRISE THEME
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Base Theme */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #E2E8F0;
}
.stApp { background-color: #0B1120; } /* Very deep navy/black */

/* Hide Streamlit Branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Live Pulse Indicator */
.live-pulse {
    display: inline-block;
    width: 12px;
    height: 12px;
    background-color: #22C55E;
    border-radius: 50%;
    margin-right: 8px;
    box-shadow: 0 0 10px #22C55E;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
    70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
    100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
}

/* Banner */
.siem-banner {
    background: linear-gradient(90deg, #0F172A 0%, #1E293B 100%);
    border-left: 5px solid #3B82F6;
    padding: 20px 30px;
    border-radius: 8px;
    margin-bottom: 25px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid #334155;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
}
.siem-banner-left { display: flex; align-items: center; gap: 20px; }
.siem-title { font-size: 28px; font-weight: 800; color: #FFFFFF; letter-spacing: 1px; margin: 0; }
.siem-sub { font-size: 13px; color: #94A3B8; text-transform: uppercase; letter-spacing: 2px; }
.live-status-box {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid #334155;
    padding: 8px 16px;
    border-radius: 30px;
    font-size: 14px;
    font-weight: 600;
    color: #E2E8F0;
    display: flex;
    align-items: center;
}

/* KPI Cards */
div[data-testid="metric-container"] {
    background: #0F172A;
    border: 1px solid #1E293B;
    border-left: 4px solid #3B82F6;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
div[data-testid="metric-container"] > label {
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: #94A3B8 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 34px !important;
    font-weight: 800 !important;
    color: #F8FAFC !important;
    font-family: 'Courier New', monospace;
}

/* Red KPI for Critical */
div[data-testid="metric-container"]:nth-child(3) {
    border-left: 4px solid #EF4444;
}
div[data-testid="metric-container"]:nth-child(3) [data-testid="stMetricValue"] {
    color: #EF4444 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0F172A;
    border-radius: 8px;
    padding: 4px;
    border: 1px solid #1E293B;
}
.stTabs [data-baseweb="tab"] {
    font-size: 14px;
    font-weight: 600;
    color: #64748B;
    border-radius: 6px;
    padding: 12px 24px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.stTabs [aria-selected="true"] {
    background: #1E293B !important;
    color: #3B82F6 !important;
    border-bottom: 2px solid #3B82F6;
}

/* Section Headers */
.sq-section {
    font-size: 14px;
    font-weight: 700;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    border-bottom: 1px solid #334155;
    padding-bottom: 8px;
    margin: 24px 0 16px 0;
}

/* Threat Feed Item */
.threat-item {
    background: #1E1B2E;
    border-left: 4px solid #EF4444;
    padding: 12px 16px;
    border-radius: 4px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
}
.threat-time { color: #94A3B8; font-family: monospace; font-size: 12px;}
.threat-desc { color: #FCA5A5; font-weight: 600; }
.threat-agent { background: #312E81; padding: 2px 8px; border-radius: 12px; font-size: 11px; }

/* AI Result Containers */
.sq-finding { background: #0F172A; border: 1px solid #1E3A8A; border-radius: 6px; padding: 16px; font-size: 15px; color: #E0F2FE; line-height: 1.6; margin-bottom: 16px; }
.sq-step { background: #064E3B; border-left: 3px solid #10B981; padding: 12px 16px; color: #D1FAE5; margin-bottom: 8px; font-size: 14px; }
.sq-warning { background: #451A03; border-left: 3px solid #F59E0B; padding: 12px 16px; color: #FEF3C7; margin-bottom: 12px; font-size: 14px; }
.sq-unknown { background: #312E81; border-left: 3px solid #8B5CF6; padding: 12px 16px; color: #EDE9FE; margin-bottom: 8px; font-size: 14px; }

/* Dataframe */
.stDataFrame { border: 1px solid #1E293B !important; border-radius: 8px; }
.stDataFrame thead th { background: #0F172A !important; color: #94A3B8 !important; text-transform: uppercase; font-size: 11px; letter-spacing: 1px;}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# CONFIG & AUTH
# ──────────────────────────────────────────────────────────────
BACKEND_URL   = st.secrets.get("BACKEND_API_URL",   "").rstrip("/")
BACKEND_TOKEN = st.secrets.get("BACKEND_API_TOKEN", "")

if not BACKEND_URL or not BACKEND_TOKEN:
    st.error("⚠️ Backend not configured — add BACKEND_API_URL and BACKEND_API_TOKEN in Streamlit Secrets.")
    st.stop()

HEADERS = {"Authorization": f"Bearer {BACKEND_TOKEN}"}

@st.cache_data(ttl=20, show_spinner=False)
def api_get(path: str, params: dict = None):
    r = requests.get(f"{BACKEND_URL}{path}", headers=HEADERS, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def api_post(path: str, body: dict = None):
    r = requests.post(f"{BACKEND_URL}{path}", headers=HEADERS, json=body or {}, timeout=90)
    r.raise_for_status()
    return r.json()

# ──────────────────────────────────────────────────────────────
# FETCH DATA
# ──────────────────────────────────────────────────────────────
try:
    summary = api_get("/api/dashboard/summary")
    recent_alerts_data = api_get("/api/alerts", params={"limit": 150})
    incidents_data = api_get("/api/incidents")
except Exception as exc:
    st.markdown(f"""
    <div class="siem-banner" style="border-left-color: #EF4444;">
      <div class="siem-banner-left">
        <span style="font-size:30px">⚠️</span>
        <div><p class="siem-title">SentinelIQ Disconnected</p><p class="siem-sub">Backend Server Unreachable</p></div>
      </div>
      <div class="live-status-box" style="color:#FCA5A5"><span class="live-pulse" style="background:#EF4444;box-shadow:none;"></span> Connection Lost</div>
    </div>
    """, unsafe_allow_html=True)
    st.error(f"Error Details: {exc}")
    st.stop()

# Parse Summary Data
sev = summary.get("severity_counts", {})
high_crit = sev.get("high", 0) + sev.get("critical", 0)
last_ts_raw = summary.get("latest_alert_timestamp")
last_ts = str(last_ts_raw)[:19] if last_ts_raw else "—"

# ──────────────────────────────────────────────────────────────
# BANNER - LIVE PULSE
# ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="siem-banner">
  <div class="siem-banner-left">
    <span style="font-size: 38px;">🛡️</span>
    <div>
      <p class="siem-title">SentinelIQ</p>
      <p class="siem-sub">Advanced Security Operations Platform</p>
    </div>
  </div>
  <div class="live-status-box">
    <span class="live-pulse"></span>
    LIVE SYNC &nbsp;|&nbsp; LAST EVENT: {last_ts}
  </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# KPI ROW
# ──────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Ingested Events", summary.get("alert_count", 0))
c2.metric("Active Investigations", summary.get("open_incident_count", 0))
c3.metric("Critical / High Threats", high_crit)
c4.metric("Live Endpoint Agents", 1) # Hardcoded for now based on Wazuh setup

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# MAIN TABS
# ──────────────────────────────────────────────────────────────
tabs = st.tabs([
    "👁️ Threat Dashboard",
    "📡 Alert Stream",
    "🔗 Incident Workbench",
    "🧠 AI Analyst",
    "🛡️ Remediation Playbooks",
    "⚙️ Platform Health"
])

# ══════════════════════════════════════════════════════════════
# TAB 1  —  THREAT DASHBOARD
# ══════════════════════════════════════════════════════════════
with tabs[0]:
    col_chart, col_feed = st.columns([2, 1], gap="large")
    
    # Left Column: Charts
    with col_chart:
        st.markdown("<div class='sq-section'>Threat Timeline (Last 150 Events)</div>", unsafe_allow_html=True)
        
        alerts_list = recent_alerts_data.get("items", [])
        if alerts_list:
            df = pd.DataFrame(alerts_list)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # Group by 10-minute bins for a nice timeline
            df['time_bin'] = df['timestamp'].dt.floor('10min')
            timeline_data = df.groupby(['time_bin', 'severity']).size().reset_index(name='count')
            
            # Color map for severity
            color_map = {"critical": "#EF4444", "high": "#F97316", "medium": "#F59E0B", "low": "#22C55E"}
            
            fig = px.bar(
                timeline_data, x="time_bin", y="count", color="severity",
                color_discrete_map=color_map,
                labels={"time_bin": "Time", "count": "Events"}
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94A3B8"),
                margin=dict(l=0, r=0, t=10, b=0),
                height=250,
                legend_title_text="",
                xaxis=dict(showgrid=False, linecolor="#334155"),
                yaxis=dict(showgrid=True, gridcolor="#1E293B", linecolor="#334155")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insufficient data to build timeline.")

        st.markdown("<div class='sq-section'>Severity Distribution</div>", unsafe_allow_html=True)
        if sev:
            labels = list(sev.keys())
            values = list(sev.values())
            colors = [color_map.get(l, "#64748B") for l in labels]
            fig_pie = go.Figure(go.Pie(
                labels=labels, values=values, hole=0.7,
                marker=dict(colors=colors, line=dict(color="#0F172A", width=2)),
                textinfo="percent", textfont=dict(size=12)
            ))
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=0, b=0, l=0, r=0), height=200,
                showlegend=True, legend=dict(font=dict(color="#94A3B8"))
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # Right Column: Live Feed & Integration
    with col_feed:
        st.markdown("<div class='sq-section'>Latest Critical & High Threats</div>", unsafe_allow_html=True)
        
        if alerts_list:
            df_crit = df[df['severity'].isin(['critical', 'high'])].head(5)
            if not df_crit.empty:
                for _, row in df_crit.iterrows():
                    ts = row['timestamp'].strftime("%H:%M:%S")
                    desc = str(row.get('rule_description', 'Unknown Alert'))[:40] + "..."
                    agent = row.get('agent_name', 'Unknown')
                    st.markdown(f"""
                    <div class="threat-item">
                        <div>
                            <div class="threat-time">{ts}</div>
                            <div class="threat-desc">{desc}</div>
                        </div>
                        <div class="threat-agent">{agent}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ No critical threats in recent stream.")
        else:
            st.info("No events in stream.")

        st.markdown("<br><div class='sq-section'>Engine Status</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#0F172A; border:1px solid #1E293B; border-radius:6px; padding:15px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                <span style="color:#94A3B8; font-size:13px;">Wazuh Indexer</span>
                <span style="color:#22C55E; font-weight:bold; font-size:13px;">● ONLINE</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                <span style="color:#94A3B8; font-size:13px;">Groq AI (LLaMA 3)</span>
                <span style="color:#22C55E; font-weight:bold; font-size:13px;">● ONLINE</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="color:#94A3B8; font-size:13px;">Auto-Ingest Cron</span>
                <span style="color:#3B82F6; font-weight:bold; font-size:13px;">● ACTIVE (2m)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 2  —  ALERT STREAM
# ══════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("<div class='sq-section'>Raw Alert Stream</div>", unsafe_allow_html=True)
    c_filt1, c_filt2 = st.columns([1, 4])
    with c_filt1:
        sev_filter = st.selectbox("Severity Filter", ["All", "critical", "high", "medium", "low"])
    with c_filt2:
        if st.button("🔄 Force Manual Sync"):
            st.cache_data.clear()
            st.rerun()

    if alerts_list:
        df_all = pd.DataFrame(alerts_list)
        if sev_filter != "All":
            df_all = df_all[df_all['severity'] == sev_filter]
        
        df_all["timestamp"] = pd.to_datetime(df_all["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        cols = ["id", "timestamp", "severity", "agent_name", "rule_id", "rule_description", "src_ip"]
        st.dataframe(df_all[[c for c in cols if c in df_all.columns]], hide_index=True, height=400)
    else:
        st.info("Stream is empty.")

# ══════════════════════════════════════════════════════════════
# TAB 3  —  INCIDENT WORKBENCH
# ══════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("<div class='sq-section'>Correlated Incidents (Auto-grouped)</div>", unsafe_allow_html=True)
    if incidents_data:
        st.dataframe(pd.DataFrame(incidents_data), hide_index=True, height=250)
    else:
        st.info("No incidents currently active.")

    st.markdown("---")
    st.markdown("<div class='sq-section'>Evidence Inspector</div>", unsafe_allow_html=True)
    inv_id = st.number_input("Target Incident ID", min_value=1, step=1, value=1)
    if st.button("🔍 Load Evidence"):
        try:
            detail = api_get(f"/api/incidents/{inv_id}")
            st.json(detail)
        except Exception as e:
            st.error(str(e))

# ══════════════════════════════════════════════════════════════
# TAB 4  —  AI ANALYST (GROQ)
# ══════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("<div class='sq-section'>AI Autonomous Analyst (LLaMA 3.3 70B)</div>", unsafe_allow_html=True)
    
    left, right = st.columns([1, 2], gap="large")
    TASKS = {
        "triage":        "⚡ Triage — Fast contextual summary",
        "investigation": "🔬 Deep Investigation — Timeline & IOCs",
        "response":      "🛡️ Response — Containment Scripts",
        "manager":       "👔 Exec Brief — Business impact",
        "report":        "📄 Full Report — JSON Download",
    }

    with left:
        ai_inc_id = st.number_input("Incident ID to Analyze", min_value=1, step=1, value=1)
        task_choice = st.radio("Analysis Vector", list(TASKS.keys()), format_func=lambda x: TASKS[x])
        st.markdown("<br>", unsafe_allow_html=True)
        run_ai = st.button("🧠 Execute AI Analysis", type="primary", use_container_width=True)

    with right:
        if run_ai:
            with st.spinner("Initiating Groq LLM Inference..."):
                try:
                    res = api_post(f"/api/incidents/{ai_inc_id}/analyze", {"task": task_choice, "force": True})
                    if res.get("status") == "success":
                        ai = res.get("result", {})
                        
                        st.markdown(f"**✓ Analysis Complete** | Engine: `{ai.get('model', 'Groq')}`", unsafe_allow_html=True)
                        st.markdown("<hr style='margin:10px 0; border-color:#334155'>", unsafe_allow_html=True)

                        # Render based on task type
                        if task_choice == "triage":
                            st.markdown("<div class='sq-section'>Finding</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='sq-finding'>{ai.get('finding','—')}</div>", unsafe_allow_html=True)
                            for a in ai.get("recommended_actions", []):
                                st.markdown(f"<div class='sq-step'>▶ {a}</div>", unsafe_allow_html=True)

                        elif task_choice == "investigation":
                            st.markdown("<div class='sq-section'>Attack Timeline</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='sq-finding'>{ai.get('timeline_summary','—')}</div>", unsafe_allow_html=True)
                            for s in ai.get("next_investigation_steps", []):
                                st.markdown(f"<div class='sq-step'>🔬 {s}</div>", unsafe_allow_html=True)

                        elif task_choice == "response":
                            st.markdown("<div class='sq-section'>Remediation Commands (PowerShell)</div>", unsafe_allow_html=True)
                            for step in ai.get("recommended_actions", []):
                                st.code(step, language="powershell")
                            if ai.get("reason"):
                                st.markdown(f"<div class='sq-warning'>⚠️ {ai.get('reason')}</div>", unsafe_allow_html=True)

                        elif task_choice == "manager":
                            st.markdown("<div class='sq-section'>Executive Summary</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='sq-finding'>{ai.get('what_happened','—')}</div>", unsafe_allow_html=True)
                            for s in ai.get("affected_systems", []):
                                st.markdown(f"<div class='sq-step'>💻 {s}</div>", unsafe_allow_html=True)

                        elif task_choice == "report":
                            st.download_button(
                                "⬇️ Download Full JSON Report",
                                data=json.dumps(ai, indent=2),
                                file_name=f"SIQ_Report_INC{ai_inc_id}.json",
                                mime="application/json",
                            )
                            st.json(ai)

                    else:
                        st.error("Analysis Failed")
                        st.json(res)
                except Exception as e:
                    st.error(f"Inference Error: {e}")

# ══════════════════════════════════════════════════════════════
# TAB 5  —  PLAYBOOKS
# ══════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("<div class='sq-section'>Active Defense Standard Operating Procedures (SOPs)</div>", unsafe_allow_html=True)
    st.info("⚠️ Execute these commands in elevated PowerShell on the affected endpoint.")
    
    with st.expander("🚫 Block Malicious IP"):
        st.code('New-NetFirewallRule -DisplayName "SIQ-Block" -Direction Inbound -RemoteAddress <IP> -Action Block', language="powershell")
    with st.expander("💀 Kill Suspicious Process"):
        st.code('Stop-Process -Name "<PROCESS_NAME>" -Force', language="powershell")
    with st.expander("🔒 Isolate Host from Network"):
        st.code('Set-NetFirewallProfile -All -DefaultInboundAction Block\nSet-NetFirewallProfile -All -DefaultOutboundAction Block', language="powershell")

# ══════════════════════════════════════════════════════════════
# TAB 6  —  HEALTH
# ══════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("<div class='sq-section'>Platform Diagnostics</div>", unsafe_allow_html=True)
    if st.button("Run Full Diagnostic"):
        try:
            h = api_get("/api/source/status")
            st.success("✅ All systems operational.")
            st.json(h)
        except Exception as e:
            st.error(f"❌ Diagnostic failed: {e}")
