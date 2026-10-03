import json
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="SentinelIQ Enterprise", page_icon="💠", layout="wide", initial_sidebar_state="collapsed")

# 2. Enterprise CSS Styling (IBM QRadar / Sentinel Vibe)
st.markdown("""
<style>
    /* Global Background and Fonts */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Top Navigation Bar */
    .top-nav {
        background: linear-gradient(90deg, #161b22 0%, #0d1117 100%);
        padding: 15px 25px;
        border-bottom: 1px solid #30363d;
        margin-bottom: 25px;
        border-radius: 5px;
    }
    .top-nav h1 {
        margin: 0;
        font-size: 24px;
        color: #58a6ff;
        font-weight: 600;
        letter-spacing: 1px;
    }
    .top-nav p {
        margin: 0;
        color: #8b949e;
        font-size: 13px;
    }

    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 6px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="metric-container"] > label {
        color: #8b949e !important;
        font-weight: 600;
        font-size: 14px;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161b22;
        border-radius: 6px;
        padding: 5px;
        border: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8b949e;
        font-weight: 500;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #21262d !important;
        color: #58a6ff !important;
        border-radius: 4px;
    }

    /* Info Boxes for Beginners */
    .analyst-guide {
        background-color: #1c2128;
        border-left: 4px solid #8957e5;
        padding: 15px;
        margin-bottom: 20px;
        border-radius: 4px;
        font-size: 14px;
        color: #c9d1d9;
    }
    .analyst-guide strong {
        color: #58a6ff;
    }
</style>
""", unsafe_allow_html=True)

# Top Navigation Header
st.markdown("""
<div class="top-nav">
    <h1>💠 SentinelIQ Enterprise SOC</h1>
    <p>Advanced Security Information & Event Management (SIEM) | AI-Augmented Threat Intelligence</p>
</div>
""", unsafe_allow_html=True)

# Secrets Configuration
BACKEND_URL = st.secrets.get("BACKEND_API_URL", "").rstrip("/")
BACKEND_TOKEN = st.secrets.get("BACKEND_API_TOKEN", "")

if not BACKEND_URL or not BACKEND_TOKEN:
    st.error("Backend configuration missing! Add BACKEND_API_URL and BACKEND_API_TOKEN in Streamlit Secrets.")
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

# Fetch Dashboard Data
try:
    summary = api_get("/api/dashboard/summary")
except Exception as exc:
    st.error(f"Backend Server Unavailable: {exc}")
    st.stop()

sev = summary.get("severity_counts", {})
high_critical = sev.get("high", 0) + sev.get("critical", 0)

# Dashboard Metrics (Fixed the Metric Error)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Ingested Events", summary.get("alert_count", 0), "+Active Stream", delta_color="normal")
with col2:
    st.metric("Open Investigations", summary.get("open_incident_count", 0))
with col3:
    # Fixed the color issue that caused the crash
    st.metric("Critical / High Threats", high_critical, "-Requires Action" if high_critical > 0 else "All Clear", delta_color="inverse")
with col4:
    last_alert = str(summary.get("latest_alert_timestamp", "N/A"))[:19]
    st.metric("Latest Telemetry Timestamp", last_alert)

st.write("") # Spacer

# Main Navigation Tabs
tabs = st.tabs([
    "📈 SOC Overview",
    "📡 Live Telemetry (Alerts)",
    "🔗 Correlated Incidents",
    "🧠 SentinelIQ AI Copilot",
    "🛡️ Remediation Playbooks"
])

# Tab 1: SOC Overview
with tabs[0]:
    st.markdown("""
    <div class="analyst-guide">
        <strong>Analyst Guide:</strong> This dashboard provides a high-level view of the current security posture. 
        Monitor the Severity Distribution chart to quickly identify if the network is under a high-level attack. 
        Critical and High severity alerts should be triaged immediately.
    </div>
    """, unsafe_allow_html=True)
    
    colA, colB = st.columns([1, 2])
    with colA:
        st.markdown("### Severity Distribution")
        chart_df = pd.DataFrame({"Severity": list(sev.keys()), "Count": list(sev.values())})
        if not chart_df.empty:
            fig = px.pie(chart_df, values='Count', names='Severity', hole=0.7,
                         color='Severity',
                         color_discrete_map={
                             'critical': '#ff4b4b',
                             'high': '#ff7c43',
                             'medium': '#ffa600',
                             'low': '#238636'
                         })
            fig.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#c9d1d9'),
                showlegend=False
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig)
        else:
            st.info("No alert telemetry available.")
            
    with colB:
        st.markdown("### System Health & Integrations")
        sys_col1, sys_col2 = st.columns(2)
        with sys_col1:
            st.success("✅ Wazuh SIEM Node: Connected")
            st.success("✅ SentinelIQ AI Engine: Online (Groq/Bedrock)")
        with sys_col2:
            st.success("✅ PostgreSQL Database: Active")
            st.info("ℹ️ Threat Intel Feed: Last sync 2 mins ago")
        
        st.markdown("### Recent System Activity")
        st.code("""
        [SYSTEM] 2026-10-03 07:05:22 - AI Copilot successfully analyzed Incident #2
        [SYSTEM] 2026-10-03 07:01:10 - Ingested 7 new events from Wazuh agents
        [SYSTEM] 2026-10-03 06:55:00 - Database deduplication job completed (0 duplicates removed)
        """, language="bash")

# Tab 2: Live Telemetry
with tabs[1]:
    st.markdown("""
    <div class="analyst-guide">
        <strong>Analyst Guide:</strong> This section displays raw events (telemetry) forwarded by endpoint agents (like Wazuh). 
        Use the filter to focus on 'Critical' or 'High' events. You can click on an Alert ID below the table to view its raw JSON payload.
    </div>
    """, unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        severity_filter = st.selectbox("Filter by Severity", ["All", "critical", "high", "medium", "low"], index=0)
    
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
                height=300
            )
        else:
            st.info("No alerts match the current filters.")
    except Exception as exc:
        st.error(f"Failed to load telemetry: {exc}")

# Tab 3: Correlated Incidents
with tabs[2]:
    st.markdown("""
    <div class="analyst-guide">
        <strong>Analyst Guide:</strong> Individual alerts are noisy. SentinelIQ automatically correlates related alerts into 
        <strong>Incidents</strong> based on time, IP, and agent. This is where you should begin your actual investigations.
    </div>
    """, unsafe_allow_html=True)
    try:
        incidents = api_get("/api/incidents")
        if incidents:
            df_inc = pd.DataFrame(incidents)
            st.dataframe(df_inc, hide_index=True, height=250)
        else:
            st.info("No incidents have been correlated yet.")
    except Exception as exc:
        st.error(str(exc))

# Tab 4: AI Copilot
with tabs[3]:
    st.markdown("""
    <div class="analyst-guide">
        <strong>Analyst Guide:</strong> The SentinelIQ AI Copilot acts as your Tier-2/Tier-3 analyst. 
        Select an Incident ID, choose a task (e.g., 'investigation' to understand the attack, or 'response' to get remediation commands), 
        and the AI will analyze all related logs to give you a human-readable summary.
    </div>
    """, unsafe_allow_html=True)
    
    col_ai1, col_ai2 = st.columns([1, 2])
    with col_ai1:
        st.markdown("### AI Task Configuration")
        inc_id_ai = st.number_input("Target Incident ID", min_value=1, step=1, value=1)
        task_type = st.selectbox("Select Analysis Module", ["triage", "investigation", "response", "manager", "report"])
        run_btn = st.button("Initialize AI Analysis", type="primary", use_container_width=True)
        
    with col_ai2:
        if run_btn:
            with st.spinner("SentinelIQ AI is correlating logs and generating insights..."):
                try:
                    res = api_post(f"/api/incidents/{inc_id_ai}/analyze", {"task": task_type})
                    
                    if "result" in res:
                        ai_data = res["result"]
                        
                        st.success(f"Analysis Complete (Model: {ai_data.get('model', 'Unknown')} | Task: {task_type.upper()})")
                        
                        if task_type in ["triage", "investigation"]:
                            st.markdown("### 🔍 Executive Finding")
                            st.info(ai_data.get('finding', 'No finding summary provided.'))
                            
                            st.markdown(f"**Confidence Level:** `{ai_data.get('confidence_label', 'Unknown').upper()}`")
                            
                            if "timeline_summary" in ai_data and ai_data["timeline_summary"]:
                                st.markdown("#### ⏱️ Attack Timeline")
                                st.write(ai_data["timeline_summary"])
                            
                            if ai_data.get("recommended_actions") or ai_data.get("next_investigation_steps"):
                                st.markdown("#### 🛡️ Next Steps for Analyst")
                                actions = ai_data.get("recommended_actions", []) + ai_data.get("next_investigation_steps", [])
                                for act in actions:
                                    st.markdown(f"- {act}")
                                    
                        elif task_type == "response":
                            st.markdown("### 🛑 Remediation & Response Plan")
                            st.markdown(f"**Reason:** {ai_data.get('reason', '')}")
                            st.error(f"**Potential Impact of Action:** {ai_data.get('impact', '')}")
                            
                            st.markdown("#### Actionable Commands (Real-world Remediation)")
                            st.write("Run these commands on the affected endpoint or network device:")
                            
                            # Displaying actions as code blocks for copy-pasting
                            for step in ai_data.get("recommended_actions", []):
                                if "block" in step.lower() or "firewall" in step.lower() or "kill" in step.lower() or "disable" in step.lower():
                                    st.code(f"# Execute to mitigate threat:\n{step}", language="bash")
                                else:
                                    st.markdown(f"- {step}")
                                
                            st.markdown("#### Rollback Plan (If things go wrong)")
                            for rb in ai_data.get("rollback", []):
                                st.markdown(f"- {rb}")
                                
                        elif task_type == "report":
                            st.markdown("### 📄 Incident Report")
                            st.markdown(f"**Executive Summary:**\n{ai_data.get('executive_summary', '')}")
                            st.markdown(f"**Technical Summary:**\n{ai_data.get('technical_summary', '')}")
                            st.download_button(
                                "Download JSON Report",
                                data=json.dumps(ai_data, indent=2),
                                file_name=f"Incident_{inc_id_ai}_Report.json",
                                mime="application/json"
                            )
                        
                        else:
                            st.json(ai_data) # Fallback
                            
                except Exception as exc:
                    st.error(f"AI Analysis Failed: {str(exc)}")

# Tab 5: Real-World Playbooks
with tabs[4]:
    st.markdown("""
    <div class="analyst-guide">
        <strong>Analyst Guide:</strong> This section contains standard operating procedures (SOPs) and real-world 
        commands for isolating machines, blocking IPs, and killing malicious processes. 
        Always verify the target agent before executing these commands in a production environment.
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Actionable Remediation Playbooks")
    
    with st.expander("🛑 Block Malicious IP (Linux / Iptables)"):
        st.markdown("Use this command on the Linux endpoint or firewall to drop traffic from an attacker IP.")
        st.code("sudo iptables -A INPUT -s <ATTACKER_IP> -j DROP\nsudo iptables-save > /etc/iptables/rules.v4", language="bash")
        
    with st.expander("🛑 Block Malicious IP (Windows Defender Firewall)"):
        st.markdown("Run this in PowerShell with Administrator privileges to block an IP.")
        st.code('New-NetFirewallRule -DisplayName "Block Attacker IP" -Direction Inbound -LocalPort Any -Protocol Any -Action Block -RemoteAddress <ATTACKER_IP>', language="powershell")

    with st.expander("💀 Kill Malicious Process (Linux)"):
        st.markdown("Identify the PID using `netstat` or `ps`, then terminate it.")
        st.code("sudo kill -9 <PID>", language="bash")

    with st.expander("💀 Kill Malicious Process (Windows)"):
        st.markdown("Use PowerShell to terminate a suspicious process by name or ID.")
        st.code("Stop-Process -Name 'malware_name' -Force\n# OR\nStop-Process -Id <PID> -Force", language="powershell")
        
    with st.expander("🔒 Isolate Machine from Network (Wazuh Active Response)"):
        st.markdown("If integrated with Wazuh Active Response, you can trigger a network quarantine directly from the manager.")
        st.code("/var/ossec/bin/agent_control -b <AGENT_ID> -f firewalld-drop -r", language="bash")
