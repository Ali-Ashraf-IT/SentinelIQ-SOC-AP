import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from datetime import datetime

# 1. Page Configuration (Must be first)
st.set_page_config(page_title="SentinelIQ SOC", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Professional Dark/Modern Look
st.markdown("""
<style>
    .reportview-container {
        background: #0E1117;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E90FF;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #A0AEC0;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #1E2130;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E90FF;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Secrets Configuration
BACKEND_URL = st.secrets.get("BACKEND_API_URL", "").rstrip("/")
BACKEND_TOKEN = st.secrets.get("BACKEND_API_TOKEN", "")

if not BACKEND_URL or not BACKEND_TOKEN:
    st.error("⚠️ Backend configuration missing! Add BACKEND_API_URL and BACKEND_API_TOKEN in Streamlit Secrets.")
    st.stop()

HEADERS = {"Authorization": f"Bearer {BACKEND_TOKEN}"}

# Helper API functions
@st.cache_data(ttl=30)
def api_get(path: str, params: dict = None):
    r = requests.get(f"{BACKEND_URL}{path}", headers=HEADERS, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def api_post(path: str, body: dict = None):
    r = requests.post(f"{BACKEND_URL}{path}", headers=HEADERS, json=body or {}, timeout=60)
    if r.status_code >= 400:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise RuntimeError(detail)
    return r.json()

# Sidebar: System Health & Info
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/shield.png", width=60)
    st.markdown("## SentinelIQ")
    st.caption("v2.0 - Professional Edition")
    st.divider()
    st.subheader("System Status")
    if st.button("🔄 Check Connection", use_container_width=True):
        try:
            health = api_get("/api/source/status")
            st.success("Connected to Backend")
        except Exception as e:
            st.error("Connection Failed")
    st.divider()
    st.markdown("© 2026 SentinelIQ SecOps")

# Main Header
st.markdown('<p class="main-header">🛡️ SentinelIQ Operations Center</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Advanced AI-Driven Threat Detection & Incident Response</p>', unsafe_allow_html=True)

# Top Metrics Row
try:
    summary = api_get("/api/dashboard/summary")
except Exception as exc:
    st.error(f"Backend Server Unavailable: {exc}")
    st.stop()

sev = summary.get("severity_counts", {})
high_critical = sev.get("high", 0) + sev.get("critical", 0)

# Dashboard Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Ingested Alerts", summary.get("alert_count", 0), "+12% today")
with col2:
    st.metric("Active Incidents", summary.get("open_incident_count", 0), "-2 resolved", delta_color="inverse")
with col3:
    st.metric("Critical / High Threats", high_critical, color="red" if high_critical > 0 else "normal")
with col4:
    last_alert = str(summary.get("latest_alert_timestamp", "N/A"))[:19]
    st.metric("Last Alert Timestamp", last_alert)

st.divider()

# Navigation Tabs
tabs = st.tabs([
    "📊 Overview & Analytics",
    "🚨 Live Alerts",
    "🔗 Correlated Incidents",
    "🤖 AI Investigator",
    "📝 Reports & Actions"
])

# Tab 1: Overview Chart (Ring/Donut Chart)
with tabs[0]:
    st.subheader("Threat Severity Distribution")
    colA, colB = st.columns([1, 2])
    
    with colA:
        chart_df = pd.DataFrame({"Severity": list(sev.keys()), "Count": list(sev.values())})
        if not chart_df.empty:
            # Create a professional Donut Chart (Ring)
            fig = px.pie(chart_df, values='Count', names='Severity', hole=0.6,
                         color='Severity',
                         color_discrete_map={
                             'critical': '#ff4b4b',
                             'high': '#ff7c43',
                             'medium': '#ffa600',
                             'low': '#003f5c'
                         })
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True)
            st.plotly_chart(fig)
        else:
            st.info("No alert data available for visualization.")
            
    with colB:
        st.markdown("### Quick Action Items")
        if high_critical > 0:
            st.error(f"⚠️ Action Required: You have {high_critical} High/Critical alerts pending review.")
        else:
            st.success("✅ System Secure: No critical alerts currently active.")
        st.info("💡 Tip: Navigate to 'AI Investigator' to automatically triage open incidents.")

# Tab 2: Live Alerts
with tabs[1]:
    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        severity_filter = st.selectbox("Severity Filter", ["All", "critical", "high", "medium", "low"], index=0)
    
    params = {"limit": 100, "offset": 0}
    if severity_filter != "All":
        params["severity"] = severity_filter
        
    try:
        data = api_get("/api/alerts", params=params)
        items = data.get("items", [])
        if items:
            df = pd.DataFrame(items)
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(
                df[["id", "timestamp", "severity", "agent_name", "rule_id", "rule_description"]],
                hide_index=True,
                height=400
            )
        else:
            st.info("No alerts match the selected filter.")
    except Exception as exc:
        st.error(f"Failed to load alerts: {exc}")

# Tab 3: Correlated Incidents
with tabs[2]:
    st.subheader("Active Investigations")
    try:
        incidents = api_get("/api/incidents")
        if incidents:
            df_inc = pd.DataFrame(incidents)
            st.dataframe(df_inc, hide_index=True)
        else:
            st.info("No incidents have been correlated yet.")
    except Exception as exc:
        st.error(str(exc))

# Tab 4: AI Investigator (Human Readable Output)
with tabs[3]:
    st.subheader("🧠 SentinelIQ AI Copilot")
    st.markdown("Select an Incident to run an automated AI analysis. The AI will translate raw logs into human-readable insights.")
    
    col_ai1, col_ai2 = st.columns([1, 2])
    with col_ai1:
        inc_id_ai = st.number_input("Enter Incident ID", min_value=1, step=1, value=1)
        task_type = st.radio("Select AI Module", ["triage", "investigation", "manager", "response"])
        run_btn = st.button("🚀 Run AI Analysis", type="primary", use_container_width=True)
        
    with col_ai2:
        if run_btn:
            with st.spinner("🧠 SentinelIQ AI is analyzing the incident..."):
                try:
                    res = api_post(f"/api/incidents/{inc_id_ai}/analyze", {"task": task_type})
                    
                    if "result" in res:
                        ai_data = res["result"]
                        
                        # Display in Human Readable Format
                        st.success("✅ Analysis Complete")
                        
                        if task_type in ["triage", "investigation"]:
                            st.markdown(f"### 🔍 Finding summary\n**{ai_data.get('finding', 'No finding summary provided.')}**")
                            
                            st.markdown(f"**Confidence Level:** `{ai_data.get('confidence_label', 'Unknown').upper()}`")
                            
                            if "timeline_summary" in ai_data and ai_data["timeline_summary"]:
                                st.markdown("#### ⏱️ Timeline")
                                st.info(ai_data["timeline_summary"])
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if ai_data.get("recommended_actions") or ai_data.get("next_investigation_steps"):
                                    st.markdown("#### 🛠️ Recommended Actions")
                                    actions = ai_data.get("recommended_actions", []) + ai_data.get("next_investigation_steps", [])
                                    for act in actions:
                                        st.markdown(f"- [ ] {act}")
                            with col_b:
                                if ai_data.get("unknowns"):
                                    st.markdown("#### ❓ Unknowns / Missing Info")
                                    for unk in ai_data.get("unknowns", []):
                                        st.markdown(f"- {unk}")
                                        
                            with st.expander("View Raw Evidence References"):
                                st.write(ai_data.get("evidence_refs", []))
                                
                        elif task_type == "manager":
                            st.markdown("### 📋 Executive Summary")
                            st.markdown(f"**What Happened:** {ai_data.get('what_happened', '')}")
                            st.markdown(f"**Business Impact:** {ai_data.get('why_it_might_matter', '')}")
                            
                            st.markdown("#### Affected Systems")
                            for sys in ai_data.get("affected_systems", []):
                                st.markdown(f"- 💻 {sys}")
                                
                        elif task_type == "response":
                            st.markdown("### 🛡️ Response & Mitigation Plan")
                            st.warning(f"**Reason for action:** {ai_data.get('reason', '')}")
                            st.error(f"**Expected Impact:** {ai_data.get('impact', '')}")
                            
                            st.markdown("#### Recommended Steps")
                            for step in ai_data.get("recommended_actions", []):
                                st.markdown(f"- ⚡ {step}")
                                
                            st.markdown("#### Rollback Plan")
                            for rb in ai_data.get("rollback", []):
                                st.markdown(f"- ⏪ {rb}")

                    else:
                        st.json(res) # Fallback if structure is unexpected
                        
                except Exception as exc:
                    st.error(f"AI Analysis Failed: {str(exc)}")

# Tab 5: Reports & Actions
with tabs[4]:
    st.subheader("Executive Incident Reports")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        inc_rep_id = st.number_input("Incident ID for Report", min_value=1, step=1, value=1)
        if st.button("📄 Generate Executive Report"):
            try:
                rep = api_post(f"/api/incidents/{inc_rep_id}/analyze", {"task": "report"})
                if "result" in rep:
                    result = rep["result"]
                    st.markdown(f"### Incident #{inc_rep_id} - Executive Report")
                    st.markdown(f"**Executive Summary:**\n{result.get('executive_summary', '')}")
                    st.markdown(f"**Technical Summary:**\n{result.get('technical_summary', '')}")
                    
                    st.download_button(
                        "⬇️ Download PDF/JSON Report",
                        data=json.dumps(result, indent=2),
                        file_name=f"SentinelIQ_Report_{inc_rep_id}.json",
                        mime="application/json"
                    )
                else:
                    st.json(rep)
            except Exception as exc:
                st.error(str(exc))
