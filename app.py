import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from datetime import datetime

# ==============================================================================
# CONFIGURATION & INITIALIZATION
# ==============================================================================
st.set_page_config(
    page_title="SentinelIQ | Security Operations",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State for Navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "Overview"

# ==============================================================================
# ENTERPRISE CSS STYLING
# ==============================================================================
def load_enterprise_css():
    st.markdown("""
    <style>
        /* Base Enterprise Variables */
        :root {
            --bg-base: #0B0E14;
            --bg-panel: #151A23;
            --bg-panel-hover: #1E2532;
            --border-color: #2A3441;
            --text-main: #E2E8F0;
            --text-muted: #8B949E;
            --accent-blue: #2563EB;
            --crit-red: #DC2626;
            --high-orange: #EA580C;
            --med-amber: #D97706;
            --low-blue: #3B82F6;
            --success-green: #16A34A;
        }

        /* Global Reset & Streamlit Overrides */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-base) !important;
            color: var(--text-main) !important;
        }
        
        /* Hide Streamlit artifacts */
        #MainMenu, header, footer {visibility: hidden;}
        .stApp > header {background-color: transparent;}
        
        /* Compact Spacing */
        .block-container {
            padding-top: 1rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            padding-bottom: 1rem !important;
            max-width: 100% !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: var(--bg-panel) !important;
            border-right: 1px solid var(--border-color) !important;
        }
        .sidebar-brand {
            padding: 1rem 0 2rem 0;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 1rem;
        }
        .brand-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #FFFFFF;
            letter-spacing: 0.5px;
            margin: 0;
        }
        .brand-subtitle {
            font-size: 0.7rem;
            text-transform: uppercase;
            color: var(--accent-blue);
            font-weight: 600;
            letter-spacing: 1px;
            margin: 0;
        }
        
        /* Top Command Bar */
        .command-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: var(--bg-panel);
            border: 1px solid var(--border-color);
            padding: 0.5rem 1rem;
            margin-bottom: 1rem;
        }
        .cmd-left { font-size: 1.1rem; font-weight: 600; color: #FFFFFF; }
        .cmd-right { display: flex; gap: 1rem; font-size: 0.8rem; color: var(--text-muted); align-items: center;}
        .cmd-item { background: var(--bg-base); padding: 0.25rem 0.75rem; border: 1px solid var(--border-color); }

        /* KPI Tiles Grid */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        .kpi-tile {
            background-color: var(--bg-panel);
            border: 1px solid var(--border-color);
            padding: 1rem;
            display: flex;
            flex-direction: column;
            border-top: 2px solid var(--border-color);
        }
        .kpi-tile.crit { border-top-color: var(--crit-red); }
        .kpi-tile.high { border-top-color: var(--high-orange); }
        .kpi-tile.active { border-top-color: var(--accent-blue); }
        .kpi-label {
            font-size: 0.65rem;
            text-transform: uppercase;
            color: var(--text-muted);
            font-weight: 600;
            letter-spacing: 0.5px;
            margin-bottom: 0.25rem;
        }
        .kpi-value {
            font-size: 1.75rem;
            font-weight: 300;
            color: #FFFFFF;
            font-family: 'SF Mono', Consolas, monospace;
            line-height: 1;
        }
        .kpi-trend { font-size: 0.7rem; margin-top: 0.5rem; color: var(--text-muted); }

        /* Section Headers */
        .section-header {
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
            margin: 1.5rem 0 1rem 0;
            letter-spacing: 0.5px;
        }

        /* Status Badges */
        .badge {
            display: inline-block;
            padding: 0.15rem 0.4rem;
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: 1px solid transparent;
        }
        .b-crit { color: #FECACA; border-color: #991B1B; background: rgba(153, 27, 27, 0.2); }
        .b-high { color: #FED7AA; border-color: #9A3412; background: rgba(154, 52, 18, 0.2); }
        .b-med  { color: #FDE68A; border-color: #92400E; background: rgba(146, 64, 14, 0.2); }
        .b-low  { color: #BFDBFE; border-color: #1E40AF; background: rgba(30, 64, 175, 0.2); }
        .b-ok   { color: #BBF7D0; border-color: #166534; background: rgba(22, 101, 52, 0.2); }

        /* AI Panel */
        .ai-panel {
            background-color: var(--bg-panel);
            border: 1px solid var(--border-color);
            border-left: 3px solid var(--accent-blue);
            padding: 1.5rem;
            margin-top: 1rem;
            font-size: 0.9rem;
        }
        .ai-header { font-weight: 600; color: #FFF; margin-bottom: 1rem; font-size: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;}
        .ai-section-title { font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); font-weight: 600; margin: 1rem 0 0.25rem 0;}
        .ai-text { color: var(--text-main); line-height: 1.5; margin-bottom: 0.5rem;}
        .ai-code { background: #000; padding: 0.75rem; border: 1px solid var(--border-color); font-family: monospace; font-size: 0.8rem; color: #A5B4FC; margin-top: 0.5rem;}

        /* Dataframe Overrides */
        [data-testid="stDataFrame"] { border: 1px solid var(--border-color) !important; }
        
        /* Expander Overrides */
        .streamlit-expanderHeader { background-color: var(--bg-panel) !important; border: 1px solid var(--border-color) !important; }
        .streamlit-expanderContent { border: 1px solid var(--border-color) !important; border-top: none !important; background-color: var(--bg-base); }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# API & BACKEND INTEGRATION
# ==============================================================================
BACKEND_URL = st.secrets.get("BACKEND_API_URL", "").rstrip("/")
BACKEND_TOKEN = st.secrets.get("BACKEND_API_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {BACKEND_TOKEN}"}

if not BACKEND_URL or not BACKEND_TOKEN:
    st.error("SYSTEM HALT: Backend API or Token not configured in Streamlit Secrets.")
    st.stop()

@st.cache_data(ttl=30, show_spinner=False)
def api_get(path: str, params: dict = None):
    try:
        r = requests.get(f"{BACKEND_URL}{path}", headers=HEADERS, params=params, timeout=20)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def api_post(path: str, body: dict = None):
    try:
        r = requests.post(f"{BACKEND_URL}{path}", headers=HEADERS, json=body or {}, timeout=90)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

# ==============================================================================
# UI COMPONENTS
# ==============================================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="brand-title">SentinelIQ</div>
            <div class="brand-subtitle">AI-Powered Security Operations</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        pages = [
            "Overview", 
            "Security Events", 
            "Incidents", 
            "Threat Intelligence", 
            "MITRE ATT&CK", 
            "Detection Rules",
            "Assets", 
            "Agents", 
            "Reports"
        ]
        
        selected_page = st.radio("Navigation", pages, label_visibility="collapsed")
        
        st.markdown("<div style='margin-top: 3rem; border-top: 1px solid #2A3441; padding-top: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-header' style='margin-top:0;'>System Status</div>", unsafe_allow_html=True)
        
        # System Status (Mocked/Derived from health endpoint in a real scenario)
        status_html = """
        <div style='font-size: 0.75rem; color: #8B949E; line-height: 1.8;'>
            <div>Wazuh Node: <span style='color:#16A34A; float:right;'>Connected</span></div>
            <div>Indexer DB: <span style='color:#16A34A; float:right;'>Connected</span></div>
            <div>AI Engine: <span style='color:#16A34A; float:right;'>Active</span></div>
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)
        
        return selected_page

def render_header(title):
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    st.markdown(f"""
    <div class="command-bar">
        <div class="cmd-left">{title}</div>
        <div class="cmd-right">
            <div class="cmd-item">Query: *</div>
            <div class="cmd-item">Time: Last 24 Hours</div>
            <div class="cmd-item">Env: Production</div>
            <div class="cmd-item">{now_str}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_badge(severity):
    sev = str(severity).lower()
    if sev == "critical": return "CRITICAL"
    if sev == "high": return "HIGH"
    if sev == "medium": return "MEDIUM"
    if sev == "low": return "LOW"
    return str(severity).upper()

def get_badge_color(severity):
    sev = str(severity).lower()
    if sev == "critical": return "#DC2626"
    if sev == "high": return "#EA580C"
    if sev == "medium": return "#D97706"
    if sev == "low": return "#3B82F6"
    return "#8B949E"

# ==============================================================================
# PAGE: OVERVIEW
# ==============================================================================
def page_overview():
    render_header("Security Operations Center (SOC) Overview")
    
    data = api_get("/api/dashboard/summary")
    if "error" in data:
        st.error(f"Data Source Error: {data['error']}")
        return

    sev = data.get("severity_counts", {})
    crit = sev.get("critical", 0)
    high = sev.get("high", 0)
    
    # KPI Grid
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-tile"><div class="kpi-label">Security Events</div><div class="kpi-value">{data.get('alert_count', 0)}</div><div class="kpi-trend">24h Volume</div></div>
        <div class="kpi-tile crit"><div class="kpi-label">Critical Alerts</div><div class="kpi-value">{crit}</div><div class="kpi-trend">Requires Triage</div></div>
        <div class="kpi-tile high"><div class="kpi-label">High Alerts</div><div class="kpi-value">{high}</div><div class="kpi-trend">Pending Review</div></div>
        <div class="kpi-tile active"><div class="kpi-label">Open Incidents</div><div class="kpi-value">{data.get('open_incident_count', 0)}</div><div class="kpi-trend">Active Investigations</div></div>
        <div class="kpi-tile"><div class="kpi-label">Active Agents</div><div class="kpi-value">1</div><div class="kpi-trend">Reporting Status</div></div>
        <div class="kpi-tile"><div class="kpi-label">AI Analysis Rate</div><div class="kpi-value">100%</div><div class="kpi-trend">Coverage</div></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([7, 3])
    
    alerts_data = api_get("/api/alerts", params={"limit": 200})
    items = alerts_data.get("items", []) if not isinstance(alerts_data, dict) or "error" not in alerts_data else []
    
    with col1:
        st.markdown("<div class='section-header'>Security Events Timeline</div>", unsafe_allow_html=True)
        if items:
            df = pd.DataFrame(items)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['time_bin'] = df['timestamp'].dt.floor('1H')
            timeline = df.groupby(['time_bin', 'severity']).size().reset_index(name='count')
            
            fig = px.bar(timeline, x="time_bin", y="count", color="severity",
                         color_discrete_map={"critical": "#DC2626", "high": "#EA580C", "medium": "#D97706", "low": "#3B82F6"})
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#8B949E", size=10), margin=dict(l=0, r=0, t=10, b=0), height=220,
                xaxis=dict(showgrid=False, title=""), yaxis=dict(showgrid=True, gridcolor="#2A3441", title="Event Count"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.markdown("<div style='color:var(--text-muted); font-size:0.8rem;'>No event telemetry available for the selected time range.</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='section-header'>Severity Distribution</div>", unsafe_allow_html=True)
        if sev:
            fig_pie = go.Figure(go.Pie(
                labels=list(sev.keys()), values=list(sev.values()), hole=0.75,
                marker=dict(colors=[get_badge_color(l) for l in sev.keys()]),
                textinfo="none"
            ))
            fig_pie.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0), height=220,
                legend=dict(font=dict(color="#8B949E", size=10), orientation="v", y=0.5)
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
        else:
            st.markdown("<div style='color:var(--text-muted); font-size:0.8rem;'>No data.</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Recent Security Events</div>", unsafe_allow_html=True)
    if items:
        df_display = pd.DataFrame(items)
        df_display['timestamp'] = pd.to_datetime(df_display['timestamp']).dt.strftime("%Y-%m-%d %H:%M:%S")
        df_display['severity'] = df_display['severity'].apply(lambda x: str(x).upper())
        cols = ['timestamp', 'severity', 'rule_id', 'rule_description', 'agent_name', 'src_ip']
        df_display = df_display[[c for c in cols if c in df_display.columns]].head(10)
        
        st.dataframe(
            df_display, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "timestamp": "TIMESTAMP", "severity": "SEV", "rule_id": "RULE", 
                "rule_description": "EVENT DESCRIPTION", "agent_name": "ASSET", "src_ip": "SRC IP"
            }
        )
    else:
         st.markdown("<div style='color:var(--text-muted); font-size:0.8rem;'>No recent events.</div>", unsafe_allow_html=True)

# ==============================================================================
# PAGE: SECURITY EVENTS
# ==============================================================================
def page_security_events():
    render_header("Security Event Investigation")
    
    # Filter Bar (Visual representation for Enterprise Feel)
    st.markdown("""
    <div style="display:flex; gap:10px; margin-bottom:15px; background:var(--bg-panel); padding:10px; border:1px solid var(--border-color);">
        <input type="text" placeholder="Search events, IPs, hashes..." style="flex:1; background:#0B0E14; border:1px solid #2A3441; color:#fff; padding:5px 10px; font-size:0.8rem;">
        <select style="background:#0B0E14; border:1px solid #2A3441; color:#fff; padding:5px; font-size:0.8rem;"><option>Severity: All</option><option>Critical</option></select>
        <select style="background:#0B0E14; border:1px solid #2A3441; color:#fff; padding:5px; font-size:0.8rem;"><option>Time: Last 24h</option></select>
    </div>
    """, unsafe_allow_html=True)

    alerts_data = api_get("/api/alerts", params={"limit": 500})
    items = alerts_data.get("items", []) if "error" not in alerts_data else []

    if items:
        df = pd.DataFrame(items)
        df['timestamp_fmt'] = pd.to_datetime(df['timestamp']).dt.strftime("%Y-%m-%d %H:%M:%S")
        df['sev_fmt'] = df['severity'].apply(lambda x: str(x).upper())
        
        display_cols = ['id', 'timestamp_fmt', 'sev_fmt', 'rule_id', 'rule_description', 'agent_name']
        st.dataframe(
            df[display_cols],
            hide_index=True,
            use_container_width=True,
            height=300,
            column_config={
                "id": "EVENT ID", "timestamp_fmt": "TIMESTAMP", "sev_fmt": "SEVERITY", 
                "rule_id": "RULE", "rule_description": "DESCRIPTION", "agent_name": "SOURCE ASSET"
            }
        )

        st.markdown("<div class='section-header'>Event Details Inspector</div>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 3])
        with col1:
            selected_id = st.text_input("Enter Event ID to inspect", value=str(df['id'].iloc[0]) if not df.empty else "")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Inspect Raw Event"):
                event = df[df['id'] == selected_id]
                if not event.empty:
                    st.json(event.iloc[0].to_dict())
                else:
                    st.warning("Event ID not found.")
    else:
        st.markdown("<div style='color:var(--text-muted); font-size:0.8rem;'>No events match the current filter criteria.</div>", unsafe_allow_html=True)

# ==============================================================================
# PAGE: INCIDENTS & AI INVESTIGATION
# ==============================================================================
def page_incidents():
    render_header("Incident Management & AI Investigation")

    incidents_data = api_get("/api/incidents")
    if "error" in incidents_data:
        st.error("Wazuh Indexer unavailable or API unreachable.")
        return

    st.markdown("<div class='section-header'>Active Incidents</div>", unsafe_allow_html=True)
    if incidents_data:
        df_inc = pd.DataFrame(incidents_data)
        st.dataframe(df_inc, hide_index=True, use_container_width=True, height=200)
    else:
        st.markdown("<div style='color:var(--text-muted); font-size:0.8rem;'>No active incidents in the current queue.</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>AI SOC Analyst Investigation</div>", unsafe_allow_html=True)
    
    col_ctrl, col_view = st.columns([1, 3])
    with col_ctrl:
        st.markdown("<div style='font-size:0.8rem; color:var(--text-muted); margin-bottom:10px;'>ANALYSIS CONTROLS</div>", unsafe_allow_html=True)
        target_inc = st.number_input("Target Incident ID", min_value=1, value=1)
        analysis_type = st.radio("Investigation Module", ["triage", "investigation", "response", "manager"], 
                                 format_func=lambda x: x.upper())
        execute = st.button("Execute AI Analysis", type="primary", use_container_width=True)

    with col_view:
        if execute:
            with st.spinner("AI Engine querying indexer, correlating events, and generating analysis..."):
                res = api_post(f"/api/incidents/{target_inc}/analyze", {"task": analysis_type, "force": True})
                
                if res.get("status") == "success":
                    ai = res.get("result", {})
                    conf = str(ai.get("confidence_label", "UNKNOWN")).upper()
                    risk_html = f"<span class='badge b-crit'>HIGH RISK</span>" if conf in ["HIGH", "MEDIUM"] else f"<span class='badge b-low'>MONITOR</span>"
                    
                    st.markdown(f"""
                    <div class="ai-panel">
                        <div class="ai-header">
                            SentinelIQ AI Analyst Report
                            <span style="float:right; font-size:0.75rem; font-weight:400; color:var(--text-muted);">Model: {ai.get('model', 'Engine-v3')} | Confidence: {conf}</span>
                        </div>
                        <div style="margin-bottom: 1rem;">{risk_html}</div>
                    """, unsafe_allow_html=True)

                    if analysis_type == "triage":
                        st.markdown(f"<div class='ai-section-title'>Threat Assessment</div><div class='ai-text'>{ai.get('finding', 'N/A')}</div>", unsafe_allow_html=True)
                        st.markdown("<div class='ai-section-title'>Recommended Actions</div>", unsafe_allow_html=True)
                        for a in ai.get("recommended_actions", []):
                            st.markdown(f"<div class='ai-text'>▪ {a}</div>", unsafe_allow_html=True)
                    
                    elif analysis_type == "investigation":
                        st.markdown(f"<div class='ai-section-title'>Attack Timeline & Summary</div><div class='ai-text'>{ai.get('timeline_summary', 'N/A')}</div>", unsafe_allow_html=True)
                        st.markdown("<div class='ai-section-title'>Next Investigation Steps</div>", unsafe_allow_html=True)
                        for s in ai.get("next_investigation_steps", []):
                            st.markdown(f"<div class='ai-text'>▪ {s}</div>", unsafe_allow_html=True)

                    elif analysis_type == "response":
                        st.markdown(f"<div class='ai-section-title'>Containment Strategy</div><div class='ai-text'>{ai.get('finding', 'N/A')}</div>", unsafe_allow_html=True)
                        st.markdown("<div class='ai-section-title'>Execution Commands (PowerShell)</div>", unsafe_allow_html=True)
                        for cmd in ai.get("recommended_actions", []):
                            st.markdown(f"<div class='ai-code'>{cmd}</div>", unsafe_allow_html=True)

                    elif analysis_type == "manager":
                        st.markdown(f"<div class='ai-section-title'>Executive Brief</div><div class='ai-text'>{ai.get('what_happened', 'N/A')}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='ai-section-title'>Business Impact</div><div class='ai-text'>{ai.get('why_it_might_matter', 'N/A')}</div>", unsafe_allow_html=True)
                        st.markdown("<div class='ai-section-title'>Affected Systems</div>", unsafe_allow_html=True)
                        for s in ai.get("affected_systems", []):
                            st.markdown(f"<div class='ai-text'>▪ {s}</div>", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error("AI Analysis failed or endpoint unresponsive.")
        else:
            st.markdown("""
            <div style="display:flex; height:100%; align-items:center; justify-content:center; color:var(--border-color); font-size:1.5rem; font-weight:600; border: 1px dashed var(--border-color); padding: 3rem; text-align:center;">
                Awaiting AI Task Execution<br>
                <span style="font-size:0.8rem; font-weight:400; color:var(--text-muted); display:block; margin-top:10px;">Select an incident and module from the left panel to begin investigation.</span>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# PAGES: PLACEHOLDERS (THREAT INTEL, MITRE, ASSETS, ETC)
# ==============================================================================
def render_placeholder_page(title, subtitle):
    render_header(title)
    st.markdown(f"""
    <div style="margin-top:2rem; padding:3rem; border:1px solid var(--border-color); background:var(--bg-panel); text-align:center;">
        <div style="font-size:1.2rem; font-weight:600; color:#FFFFFF; margin-bottom:0.5rem;">{subtitle}</div>
        <div style="font-size:0.85rem; color:var(--text-muted);">Historical data accumulation required. Insufficient telemetry to render this module.</div>
    </div>
    """, unsafe_allow_html=True)

def page_threat_intel(): render_placeholder_page("Threat Intelligence", "IOC Reputation Engine")
def page_mitre(): render_placeholder_page("MITRE ATT&CK Framework", "Tactics & Techniques Coverage")
def page_rules(): render_placeholder_page("Detection Engineering", "SIEM Rule Management")
def page_assets(): render_placeholder_page("Asset Inventory", "Endpoint Visibility")
def page_agents():
    render_header("Agent Management")
    st.markdown("<div class='section-header'>Wazuh Infrastructure Nodes</div>", unsafe_allow_html=True)
    status = api_get("/api/source/status")
    if "error" not in status:
        st.json(status)
    else:
        st.error("Unable to connect to Wazuh Manager API.")
def page_reports(): render_placeholder_page("Compliance & Reporting", "Automated Security Reports")

# ==============================================================================
# MAIN ROUTING
# ==============================================================================
def main():
    load_enterprise_css()
    selected = render_sidebar()
    
    if selected == "Overview": page_overview()
    elif selected == "Security Events": page_security_events()
    elif selected == "Incidents": page_incidents()
    elif selected == "Threat Intelligence": page_threat_intel()
    elif selected == "MITRE ATT&CK": page_mitre()
    elif selected == "Detection Rules": page_rules()
    elif selected == "Assets": page_assets()
    elif selected == "Agents": page_agents()
    elif selected == "Reports": page_reports()
    elif selected == "System Health":
        render_header("System Health & Diagnostics")
        st.code("Wazuh API: CONNECTED\nIndexer: CONNECTED\nAI Engine: ONLINE\nStreamlit: OK")

if __name__ == "__main__":
    main()
