"""
SentinelIQ - Enterprise Security Operations Platform
Production-ready SIEM dashboard built on Streamlit
"""

import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from datetime import datetime, timezone

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SentinelIQ SOC Platform",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────────
if "nav" not in st.session_state:
    st.session_state.nav = "Overview"

# ──────────────────────────────────────────────────────────────────────────────
# ENTERPRISE CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts & Reset ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #0D1117 !important;
    color: #C9D1D9 !important;
}

/* ── Hide Streamlit chrome ─────────────────────────────────────────────── */
#MainMenu, footer, header, [data-testid="stToolbar"] { visibility: hidden; height: 0; }

/* ── Main container padding ────────────────────────────────────────────── */
.block-container {
    padding: 0.75rem 1.5rem 1rem 1.5rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #161B22 !important;
    border-right: 1px solid #21262D !important;
    padding: 0 !important;
    min-width: 220px !important;
    max-width: 220px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* ── Sidebar brand header ───────────────────────────────────────────────── */
.siq-brand {
    padding: 1.25rem 1rem 1rem 1rem;
    border-bottom: 1px solid #21262D;
}
.siq-brand-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #E6EDF3;
    letter-spacing: 0.3px;
}
.siq-brand-sub {
    font-size: 0.65rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #388BFD;
    margin-top: 2px;
}

/* ── Nav group label ────────────────────────────────────────────────────── */
.nav-group {
    font-size: 0.6rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #484F58;
    padding: 1rem 1rem 0.3rem 1rem;
}

/* ── Nav buttons ────────────────────────────────────────────────────────── */
.stButton > button {
    width: 100% !important;
    text-align: left !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    color: #8B949E !important;
    font-size: 0.82rem !important;
    font-weight: 400 !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.15s !important;
    box-shadow: none !important;
    justify-content: flex-start !important;
}
.stButton > button:hover {
    background: rgba(56, 139, 253, 0.1) !important;
    color: #E6EDF3 !important;
}
.nav-active .stButton > button {
    background: rgba(56, 139, 253, 0.15) !important;
    color: #79C0FF !important;
    border-left: 2px solid #388BFD !important;
    font-weight: 500 !important;
}

/* ── System status sidebar ──────────────────────────────────────────────── */
.sys-status {
    position: absolute;
    bottom: 0;
    width: 100%;
    padding: 0.75rem 1rem;
    border-top: 1px solid #21262D;
    background: #161B22;
}
.sys-label { font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.8px; color: #484F58; margin-bottom: 0.5rem; font-weight: 600;}
.sys-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px; font-size: 0.72rem; color: #8B949E; }
.sys-dot-green { width: 6px; height: 6px; border-radius: 50%; background: #3FB950; display: inline-block; margin-right: 4px; }
.sys-dot-red   { width: 6px; height: 6px; border-radius: 50%; background: #F85149; display: inline-block; margin-right: 4px; }
.sys-status-ok { color: #3FB950; font-size: 0.7rem; font-weight: 500; }

/* ── Top Command Bar ────────────────────────────────────────────────────── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #161B22;
    border: 1px solid #21262D;
    padding: 0.5rem 1rem;
    margin-bottom: 1rem;
    border-radius: 0;
}
.topbar-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #E6EDF3;
}
.topbar-right {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}
.topbar-chip {
    background: #0D1117;
    border: 1px solid #30363D;
    color: #8B949E;
    font-size: 0.7rem;
    padding: 0.2rem 0.6rem;
    border-radius: 3px;
    font-family: 'JetBrains Mono', monospace;
}
.topbar-live {
    display: flex;
    align-items: center;
    gap: 5px;
    background: rgba(63, 185, 80, 0.1);
    border: 1px solid rgba(63, 185, 80, 0.3);
    color: #3FB950;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: 3px;
}
.live-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #3FB950;
    animation: livepulse 1.8s ease-in-out infinite;
}
@keyframes livepulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ── KPI Row ────────────────────────────────────────────────────────────── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}
.kpi-card {
    background: #161B22;
    border: 1px solid #21262D;
    padding: 0.875rem 1rem;
    border-top: 2px solid #30363D;
    position: relative;
}
.kpi-card.danger  { border-top-color: #F85149; }
.kpi-card.warning { border-top-color: #D29922; }
.kpi-card.info    { border-top-color: #388BFD; }
.kpi-card.success { border-top-color: #3FB950; }
.kpi-label { font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; color: #484F58; margin-bottom: 0.35rem; }
.kpi-value { font-size: 1.8rem; font-weight: 300; color: #E6EDF3; font-family: 'JetBrains Mono', monospace; line-height: 1.1; }
.kpi-sub   { font-size: 0.65rem; color: #484F58; margin-top: 0.35rem; }

/* ── Section divider ────────────────────────────────────────────────────── */
.sec-header {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #484F58;
    border-bottom: 1px solid #21262D;
    padding-bottom: 0.4rem;
    margin: 1.25rem 0 0.75rem 0;
}

/* ── Severity Badges ────────────────────────────────────────────────────── */
.sev-badge {
    display: inline-block;
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 0.15rem 0.45rem;
    border-radius: 2px;
}
.sev-crit { background: rgba(248, 81, 73, 0.15); color: #FF7B72; border: 1px solid rgba(248, 81, 73, 0.3); }
.sev-high { background: rgba(210, 153, 34, 0.15); color: #E3B341; border: 1px solid rgba(210, 153, 34, 0.3); }
.sev-med  { background: rgba(56, 139, 253, 0.15); color: #79C0FF; border: 1px solid rgba(56, 139, 253, 0.3); }
.sev-low  { background: rgba(63, 185, 80, 0.15);  color: #56D364; border: 1px solid rgba(63, 185, 80, 0.3); }
.sev-unk  { background: rgba(72, 79, 88, 0.3);    color: #8B949E; border: 1px solid #30363D; }

/* ── Incident Row ───────────────────────────────────────────────────────── */
.inc-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.inc-table th {
    background: #0D1117;
    color: #484F58;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 0.5rem 0.75rem;
    text-align: left;
    border-bottom: 1px solid #21262D;
}
.inc-table td {
    padding: 0.6rem 0.75rem;
    border-bottom: 1px solid #161B22;
    color: #C9D1D9;
    vertical-align: middle;
}
.inc-table tr:hover td { background: #1C2128; }

/* ── Event Table ────────────────────────────────────────────────────────── */
.evt-table { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
.evt-table th {
    background: #0D1117;
    color: #484F58;
    font-size: 0.6rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 0.4rem 0.75rem;
    text-align: left;
    border-bottom: 1px solid #21262D;
    white-space: nowrap;
}
.evt-table td {
    padding: 0.45rem 0.75rem;
    border-bottom: 1px solid #161B22;
    color: #C9D1D9;
    white-space: nowrap;
}
.evt-table tr:hover td { background: #1C2128; cursor: pointer; }
.ts-cell  { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #8B949E; }
.rule-id  { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #6E7681; }
.desc-cell { max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #C9D1D9; }
.agent-cell { color: #79C0FF; font-size: 0.75rem; }
.ip-cell  { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #8B949E; }

/* ── AI Panel ───────────────────────────────────────────────────────────── */
.ai-container {
    background: #0D1117;
    border: 1px solid #21262D;
    border-radius: 4px;
    overflow: hidden;
}
.ai-header-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #161B22;
    border-bottom: 1px solid #21262D;
    padding: 0.65rem 1rem;
}
.ai-header-title { font-size: 0.8rem; font-weight: 600; color: #E6EDF3; }
.ai-header-meta  { font-size: 0.68rem; color: #484F58; font-family: 'JetBrains Mono', monospace; }
.ai-body { padding: 1rem; }
.ai-risk-crit { display: inline-block; background: rgba(248,81,73,0.15); color: #FF7B72; border: 1px solid rgba(248,81,73,0.4); font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; padding: 0.2rem 0.6rem; border-radius: 2px; margin-bottom: 1rem; }
.ai-risk-high { display: inline-block; background: rgba(210,153,34,0.15); color: #E3B341; border: 1px solid rgba(210,153,34,0.4); font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; padding: 0.2rem 0.6rem; border-radius: 2px; margin-bottom: 1rem; }
.ai-risk-med  { display: inline-block; background: rgba(56,139,253,0.15); color: #79C0FF; border: 1px solid rgba(56,139,253,0.4); font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; padding: 0.2rem 0.6rem; border-radius: 2px; margin-bottom: 1rem; }
.ai-section-label { font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #388BFD; margin: 1rem 0 0.35rem 0; }
.ai-body-text { font-size: 0.82rem; color: #C9D1D9; line-height: 1.65; }
.ai-action { background: #161B22; border-left: 2px solid #388BFD; padding: 0.5rem 0.75rem; margin-bottom: 0.4rem; font-size: 0.8rem; color: #C9D1D9; line-height: 1.5; }
.ai-code-block { background: #0D1117; border: 1px solid #30363D; padding: 0.75rem 1rem; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #A5D6FF; margin-bottom: 0.4rem; white-space: pre-wrap; word-break: break-all; }
.ai-gap { background: #161B22; border-left: 2px solid #484F58; padding: 0.5rem 0.75rem; margin-bottom: 0.4rem; font-size: 0.8rem; color: #8B949E; }

/* ── Control Panel ──────────────────────────────────────────────────────── */
.ctrl-panel {
    background: #161B22;
    border: 1px solid #21262D;
    padding: 1rem;
    height: 100%;
}
.ctrl-label { font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; color: #484F58; margin-bottom: 0.4rem; }

/* ── Streamlit Widget Overrides ─────────────────────────────────────────── */
[data-testid="stDataFrame"] { border: 1px solid #21262D !important; border-radius: 0 !important; }
.stSelectbox > label, .stRadio > label, .stNumberInput > label { font-size: 0.68rem !important; text-transform: uppercase !important; letter-spacing: 0.8px !important; color: #484F58 !important; font-weight: 600 !important; }
.stTextInput input, .stNumberInput input {
    background: #0D1117 !important;
    border: 1px solid #30363D !important;
    color: #C9D1D9 !important;
    border-radius: 3px !important;
    font-size: 0.82rem !important;
}
div[data-testid="metric-container"] { display: none; }  /* hide default metrics */
.stRadio [data-testid="stMarkdownContainer"] p { font-size: 0.8rem !important; color: #8B949E !important; }
.stSpinner > div { border-color: #388BFD transparent transparent transparent !important; }

/* Primary button override for nav only */
.stButton > button[kind="primary"] {
    background: #388BFD !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 3px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    width: 100% !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1F6FEB !important;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# BACKEND CONNECTION
# ──────────────────────────────────────────────────────────────────────────────
BACKEND_URL   = st.secrets.get("BACKEND_API_URL",   "").rstrip("/")
BACKEND_TOKEN = st.secrets.get("BACKEND_API_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {BACKEND_TOKEN}"}

if not BACKEND_URL or not BACKEND_TOKEN:
    st.error("SYSTEM HALT: BACKEND_API_URL or BACKEND_API_TOKEN not configured in Streamlit Secrets.")
    st.stop()

@st.cache_data(ttl=30, show_spinner=False)
def api_get(path: str, params: dict = None):
    try:
        r = requests.get(f"{BACKEND_URL}{path}", headers=HEADERS, params=params, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"__error__": str(e)}

def api_post(path: str, body: dict = None):
    try:
        r = requests.post(f"{BACKEND_URL}{path}", headers=HEADERS, json=body or {}, timeout=90)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ──────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────
def fmt_ts(ts_raw):
    """Format ISO timestamp to readable format."""
    try:
        dt = pd.to_datetime(ts_raw)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts_raw)[:19]

def sev_badge(sev):
    """Return an HTML severity badge."""
    s = str(sev).lower()
    if s == "critical": return "<span class='sev-badge sev-crit'>CRITICAL</span>"
    if s == "high":     return "<span class='sev-badge sev-high'>HIGH</span>"
    if s == "medium":   return "<span class='sev-badge sev-med'>MEDIUM</span>"
    if s == "low":      return "<span class='sev-badge sev-low'>LOW</span>"
    return "<span class='sev-badge sev-unk'>UNKNOWN</span>"

def sev_color(sev):
    s = str(sev).lower()
    return {"critical": "#F85149", "high": "#D29922", "medium": "#388BFD", "low": "#3FB950"}.get(s, "#484F58")

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR (radio-based nav — more reliable in Streamlit)
# ──────────────────────────────────────────────────────────────────────────────
ALL_PAGES = [
    "Overview", "Security Events", "Incidents",
    "Threat Intelligence", "MITRE ATT&CK", "Detection Rules",
    "Assets", "Agents", "Reports"
]

def render_sidebar():
    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="padding:1rem 1rem 0.75rem 1rem; border-bottom:1px solid #21262D;">
            <div style="font-size:1.1rem;font-weight:700;color:#E6EDF3;letter-spacing:0.3px;">SentinelIQ</div>
            <div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;letter-spacing:1.2px;color:#388BFD;margin-top:2px;white-space:nowrap;">AI-Powered Security Operations</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation via radio (hidden native, styled via CSS)
        st.markdown("<div style='margin-top:0.75rem;'>", unsafe_allow_html=True)
        selected = st.radio(
            "nav",
            ALL_PAGES,
            index=ALL_PAGES.index(st.session_state.nav) if st.session_state.nav in ALL_PAGES else 0,
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)
        if selected != st.session_state.nav:
            st.session_state.nav = selected
            st.rerun()

        # System Status pinned at bottom
        st.markdown("""
        <div style="position:fixed;bottom:0;width:220px;padding:0.75rem 1rem;
                    border-top:1px solid #21262D;background:#161B22;">
            <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.8px;
                        color:#484F58;margin-bottom:0.5rem;font-weight:600;">System Status</div>
            <div style="font-size:0.72rem;color:#8B949E;line-height:1.8;">
                <div style="display:flex;justify-content:space-between;">
                    <span>&#9679; Wazuh Node</span><span style="color:#3FB950;">Online</span>
                </div>
                <div style="display:flex;justify-content:space-between;">
                    <span>&#9679; Indexer</span><span style="color:#3FB950;">Connected</span>
                </div>
                <div style="display:flex;justify-content:space-between;">
                    <span>&#9679; AI Engine</span><span style="color:#3FB950;">Active</span>
                </div>
                <div style="display:flex;justify-content:space-between;">
                    <span>&#9679; Ingest Cron</span><span style="color:#388BFD;">2m cycle</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# TOPBAR
# ──────────────────────────────────────────────────────────────────────────────
def render_topbar(title):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    st.markdown(f"""
    <div class="topbar">
        <div class="topbar-title">{title}</div>
        <div class="topbar-right">
            <div class="topbar-chip">Last 24 Hours</div>
            <div class="topbar-chip">Production</div>
            <div class="topbar-chip">{now}</div>
            <div class="topbar-live">
                <div class="live-dot"></div>
                LIVE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# KPI ROW
# ──────────────────────────────────────────────────────────────────────────────
def render_kpi_row(summary):
    sev = summary.get("severity_counts", {})
    crit = sev.get("critical", 0)
    high = sev.get("high", 0)
    med  = sev.get("medium", 0)
    low  = sev.get("low", 0)
    total = summary.get("alert_count", 0)
    open_inc = summary.get("open_incident_count", 0)

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-label">Security Events</div>
            <div class="kpi-value">{total:,}</div>
            <div class="kpi-sub">Total ingested</div>
        </div>
        <div class="kpi-card danger">
            <div class="kpi-label">Critical</div>
            <div class="kpi-value">{crit}</div>
            <div class="kpi-sub">Immediate triage</div>
        </div>
        <div class="kpi-card warning">
            <div class="kpi-label">High</div>
            <div class="kpi-value">{high}</div>
            <div class="kpi-sub">Pending review</div>
        </div>
        <div class="kpi-card info">
            <div class="kpi-label">Medium / Low</div>
            <div class="kpi-value">{med + low}</div>
            <div class="kpi-sub">Monitoring</div>
        </div>
        <div class="kpi-card info">
            <div class="kpi-label">Open Incidents</div>
            <div class="kpi-value">{open_inc}</div>
            <div class="kpi-sub">Active investigations</div>
        </div>
        <div class="kpi-card success">
            <div class="kpi-label">Agents Online</div>
            <div class="kpi-value">1</div>
            <div class="kpi-sub">Wazuh endpoints</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# EVENT TABLE (HTML-rendered, dense, professional)
# ──────────────────────────────────────────────────────────────────────────────
def render_event_table(items, max_rows=50):
    if not items:
        st.markdown("<div style='padding:1.5rem; color:#484F58; font-size:0.82rem; background:#161B22; border:1px solid #21262D;'>No security events for the selected criteria.</div>", unsafe_allow_html=True)
        return

    rows_html = ""
    for item in items[:max_rows]:
        sev = str(item.get("severity", "unknown")).lower()
        badge = sev_badge(sev)
        ts    = fmt_ts(item.get("timestamp", ""))
        rule  = item.get("rule_id", "—")
        desc  = str(item.get("rule_description") or "—")[:65]
        agent = item.get("agent_name", "—")
        src   = item.get("src_ip", "—") or "—"
        eid   = item.get("id", "—")
        rows_html += f"""
        <tr>
            <td class="ts-cell">{ts}</td>
            <td>{badge}</td>
            <td class="rule-id">{rule}</td>
            <td class="desc-cell" title="{desc}">{desc}</td>
            <td class="agent-cell">{agent}</td>
            <td class="ip-cell">{src}</td>
            <td class="rule-id">{eid}</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto; background:#161B22; border:1px solid #21262D;">
    <table class="evt-table">
        <thead>
            <tr>
                <th>Timestamp</th>
                <th>Severity</th>
                <th>Rule ID</th>
                <th>Description</th>
                <th>Asset</th>
                <th>Src IP</th>
                <th>Event ID</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    </div>
    <div style="font-size:0.68rem; color:#484F58; margin-top:0.4rem; padding-left:0.25rem;">
        Showing {min(len(items), max_rows)} of {len(items)} events
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# INCIDENT TABLE
# ──────────────────────────────────────────────────────────────────────────────
def render_incident_table(incidents):
    if not incidents:
        st.markdown("<div style='padding:1.5rem; color:#484F58; font-size:0.82rem; background:#161B22; border:1px solid #21262D;'>No active incidents in the current queue.</div>", unsafe_allow_html=True)
        return

    rows_html = ""
    for inc in incidents[:30]:
        sev   = str(inc.get("severity", "unknown")).lower()
        badge = sev_badge(sev)
        iid   = inc.get("id", "—")
        title = str(inc.get("title", "Untitled"))[:55]
        status = str(inc.get("status", "open")).upper()
        first = fmt_ts(inc.get("first_seen", ""))
        last  = fmt_ts(inc.get("last_seen", ""))
        cnt   = inc.get("repeat_count", inc.get("alert_count", "—"))
        rows_html += f"""
        <tr>
            <td class="rule-id">INC-{iid}</td>
            <td>{badge}</td>
            <td class="desc-cell">{title}</td>
            <td><span style="background:#1C2128; border:1px solid #30363D; font-size:0.65rem; padding:0.15rem 0.4rem; color:#8B949E; font-weight:600;">{status}</span></td>
            <td class="ts-cell">{first}</td>
            <td class="ts-cell">{last}</td>
            <td class="rule-id">{cnt}</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto; background:#161B22; border:1px solid #21262D;">
    <table class="inc-table">
        <thead>
            <tr>
                <th>Incident ID</th>
                <th>Severity</th>
                <th>Title</th>
                <th>Status</th>
                <th>First Seen</th>
                <th>Last Seen</th>
                <th>Event Count</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# AI INVESTIGATION PANEL
# ──────────────────────────────────────────────────────────────────────────────
def render_ai_result(ai, task, model_name, confidence):
    conf = str(confidence).upper()
    risk_cls = "ai-risk-crit" if conf == "HIGH" else ("ai-risk-high" if conf == "MEDIUM" else "ai-risk-med")
    risk_label = "HIGH RISK" if conf == "HIGH" else ("MEDIUM RISK" if conf == "MEDIUM" else "LOW RISK")

    st.markdown(f"""
    <div class="ai-container">
        <div class="ai-header-bar">
            <div class="ai-header-title">SentinelIQ AI Analyst — {task.upper()}</div>
            <div class="ai-header-meta">Engine: {model_name} &nbsp;|&nbsp; Confidence: {conf}</div>
        </div>
        <div class="ai-body">
            <span class="{risk_cls}">{risk_label}</span>
    """, unsafe_allow_html=True)

    def section(label, text):
        if text:
            st.markdown(f"""
            <div class="ai-section-label">{label}</div>
            <div class="ai-body-text">{text}</div>
            """, unsafe_allow_html=True)

    def action_list(label, items):
        if items:
            rows = "".join(f"<div class='ai-action'>▪ {a}</div>" for a in items)
            st.markdown(f"<div class='ai-section-label'>{label}</div>{rows}", unsafe_allow_html=True)

    def gap_list(label, items):
        if items:
            rows = "".join(f"<div class='ai-gap'>? {a}</div>" for a in items)
            st.markdown(f"<div class='ai-section-label'>{label}</div>{rows}", unsafe_allow_html=True)

    if task == "triage":
        section("Threat Assessment", ai.get("finding"))
        action_list("Recommended Actions", ai.get("recommended_actions", []))
        gap_list("Evidence Gaps", ai.get("unknowns", []))

    elif task == "investigation":
        section("Analyst Finding", ai.get("finding"))
        section("Attack Timeline", ai.get("timeline_summary"))
        action_list("Next Investigation Steps", ai.get("next_investigation_steps", []) + ai.get("recommended_actions", []))
        gap_list("Open Questions", ai.get("unknowns", []))

    elif task == "response":
        section("Threat Summary", ai.get("finding"))
        if ai.get("reason"):
            st.markdown(f"<div class='ai-section-label'>Why Act Now</div><div class='ai-body-text'>{ai.get('reason')}</div>", unsafe_allow_html=True)
        if ai.get("impact"):
            st.markdown(f"<div class='ai-section-label'>Potential Impact</div><div class='ai-body-text'>{ai.get('impact')}</div>", unsafe_allow_html=True)
        if ai.get("recommended_actions"):
            st.markdown("<div class='ai-section-label'>Containment Commands (PowerShell)</div>", unsafe_allow_html=True)
            for cmd in ai.get("recommended_actions", []):
                st.markdown(f"<div class='ai-code-block'>{cmd}</div>", unsafe_allow_html=True)
        action_list("Verification Steps", ai.get("verification", []))

    elif task == "manager":
        section("Executive Summary", ai.get("what_happened"))
        section("Business Impact", ai.get("why_it_might_matter"))
        action_list("Affected Systems", ai.get("affected_systems", []))
        action_list("Confirmed Facts", ai.get("what_we_know", []))
        gap_list("Open Investigation Points", ai.get("what_we_do_not_know", []))

    elif task == "report":
        section("Executive Summary", ai.get("executive_summary"))
        section("Technical Summary", ai.get("technical_summary"))
        if ai.get("timeline"):
            rows = "".join(f"<div class='ai-action'>⏱ {t}</div>" for t in ai.get("timeline", []))
            st.markdown(f"<div class='ai-section-label'>Incident Timeline</div>{rows}", unsafe_allow_html=True)
        st.download_button(
            "Download Full Report (JSON)",
            data=json.dumps(ai, indent=2, default=str),
            file_name=f"SentinelIQ_Report.json",
            mime="application/json",
        )

    st.markdown("</div></div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# PAGE: OVERVIEW
# ──────────────────────────────────────────────────────────────────────────────
def page_overview():
    render_topbar("Security Operations Center — Overview")

    # Load data
    summary = api_get("/api/dashboard/summary")
    if "__error__" in summary:
        st.error(f"Wazuh API Unavailable: {summary['__error__']}")
        return

    render_kpi_row(summary)

    alerts_resp = api_get("/api/alerts", params={"limit": 200})
    items = alerts_resp.get("items", []) if "__error__" not in alerts_resp else []

    col_l, col_r = st.columns([7, 3])

    with col_l:
        st.markdown("<div class='sec-header'>Security Events Timeline</div>", unsafe_allow_html=True)
        if items:
            df = pd.DataFrame(items)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['time_bin'] = df['timestamp'].dt.floor('h')
            tl = df.groupby(['time_bin', 'severity']).size().reset_index(name='count')

            color_map = {"critical": "#F85149", "high": "#D29922", "medium": "#388BFD", "low": "#3FB950"}
            fig = px.bar(tl, x="time_bin", y="count", color="severity",
                         color_discrete_map=color_map,
                         labels={"time_bin": "", "count": "Events"})
            fig.update_layout(
                plot_bgcolor="#0D1117", paper_bgcolor="#0D1117",
                font=dict(color="#8B949E", size=10),
                margin=dict(l=0, r=0, t=5, b=0), height=200,
                xaxis=dict(showgrid=False, linecolor="#21262D", tickfont=dict(size=9)),
                yaxis=dict(showgrid=True, gridcolor="#161B22", linecolor="#21262D"),
                legend=dict(orientation="h", y=1.15, x=0, font=dict(size=9)),
                bargap=0.15,
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.markdown("<div style='padding:1rem; color:#484F58; font-size:0.8rem;'>No telemetry available for timeline.</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown("<div class='sec-header'>Severity Distribution</div>", unsafe_allow_html=True)
        sev = summary.get("severity_counts", {})
        if sev:
            labels = list(sev.keys())
            values = list(sev.values())
            fig2 = go.Figure(go.Pie(
                labels=labels, values=values, hole=0.72,
                marker=dict(colors=[sev_color(l) for l in labels]),
                textinfo="none",
            ))
            fig2.update_layout(
                paper_bgcolor="#0D1117", plot_bgcolor="#0D1117",
                margin=dict(l=0, r=0, t=5, b=0), height=200,
                legend=dict(font=dict(color="#8B949E", size=9), orientation="v"),
                showlegend=True,
            )
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<div class='sec-header'>Recent Security Events</div>", unsafe_allow_html=True)
    render_event_table(items, max_rows=15)

# ──────────────────────────────────────────────────────────────────────────────
# PAGE: SECURITY EVENTS
# ──────────────────────────────────────────────────────────────────────────────
def page_security_events():
    render_topbar("Security Events — Investigation")

    # Filter bar
    fc1, fc2, fc3 = st.columns([2, 1, 1])
    with fc1:
        sev_filter = st.selectbox("Severity", ["All", "critical", "high", "medium", "low"], label_visibility="collapsed")
    with fc2:
        limit = st.selectbox("Max Results", [100, 250, 500], label_visibility="collapsed")
    with fc3:
        if st.button("Refresh Stream", type="primary"):
            st.cache_data.clear()
            st.rerun()

    params = {"limit": limit}
    if sev_filter != "All":
        params["severity"] = sev_filter

    resp = api_get("/api/alerts", params=params)
    items = resp.get("items", []) if "__error__" not in resp else []

    st.markdown("<div class='sec-header'>Security Event Stream</div>", unsafe_allow_html=True)
    render_event_table(items, max_rows=limit)

    # Event inspector
    st.markdown("<div class='sec-header'>Event Detail Inspector</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 3])
    with col1:
        default_id = str(items[0].get("id", 1)) if items else "1"
        inspect_id = st.text_input("Event ID", value=default_id)
    with col2:
        if items:
            matches = [x for x in items if str(x.get("id", "")) == inspect_id]
            if matches:
                ev = matches[0]
                with st.expander("Event Details", expanded=True):
                    meta_col, raw_col = st.columns([1, 1])
                    with meta_col:
                        st.markdown(f"""
                        **Timestamp:** `{fmt_ts(ev.get('timestamp', ''))}`  
                        **Severity:** {sev_badge(ev.get('severity', 'unknown'))}  
                        **Rule ID:** `{ev.get('rule_id', '—')}`  
                        **Description:** {ev.get('rule_description', '—')}  
                        **Agent:** `{ev.get('agent_name', '—')}`  
                        **Source IP:** `{ev.get('src_ip', '—')}`  
                        **Destination IP:** `{ev.get('dst_ip', '—')}`
                        """, unsafe_allow_html=True)
                    with raw_col:
                        st.json(ev)
            else:
                st.warning("Event ID not found in current result set.")

# ──────────────────────────────────────────────────────────────────────────────
# PAGE: INCIDENTS
# ──────────────────────────────────────────────────────────────────────────────
def page_incidents():
    render_topbar("Incident Management — AI Investigation")

    resp = api_get("/api/incidents")
    incidents = resp if isinstance(resp, list) else []

    st.markdown("<div class='sec-header'>Active Incidents</div>", unsafe_allow_html=True)
    render_incident_table(incidents)

    st.markdown("<div class='sec-header'>AI SOC Analyst</div>", unsafe_allow_html=True)

    ctrl_col, result_col = st.columns([1, 3])

    with ctrl_col:
        st.markdown("""
        <div class="ctrl-panel">
        <div class="ctrl-label">Analysis Controls</div>
        </div>
        """, unsafe_allow_html=True)
        target_id = st.number_input("Incident ID", min_value=1, value=1)
        task = st.radio("Analysis Module", ["triage", "investigation", "response", "manager", "report"],
                        format_func=lambda x: x.upper())
        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("Execute AI Analysis", type="primary", use_container_width=True)

    with result_col:
        if run:
            with st.spinner("Querying Wazuh indexer and running AI inference..."):
                res = api_post(f"/api/incidents/{target_id}/analyze", {"task": task, "force": True})

            if res.get("status") == "success":
                ai = res.get("result", {})
                render_ai_result(
                    ai=ai,
                    task=task,
                    model_name=ai.get("model", "Groq LLaMA"),
                    confidence=ai.get("confidence_label", "MEDIUM"),
                )
            elif res.get("status") == "error":
                st.error(f"AI Engine Error: {res.get('message', 'Unknown error')}")
            else:
                st.error(f"Unexpected response: {res}")
        else:
            st.markdown("""
            <div style="display:flex; flex-direction:column; align-items:center; justify-content:center;
                        height:300px; background:#161B22; border:1px solid #21262D; color:#484F58;">
                <div style="font-size:0.9rem; font-weight:600; margin-bottom:0.5rem;">AI Analyst — Idle</div>
                <div style="font-size:0.75rem; text-align:center;">
                    Select an incident and analysis module,<br>then press Execute.
                </div>
            </div>
            """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# PAGE: AGENTS
# ──────────────────────────────────────────────────────────────────────────────
def page_agents():
    render_topbar("Agent Management — Wazuh Infrastructure")
    st.markdown("<div class='sec-header'>Wazuh Agent Registry</div>", unsafe_allow_html=True)

    resp = api_get("/api/source/status")
    if "__error__" in resp:
        st.error(f"Cannot reach Wazuh Manager API: {resp['__error__']}")
        return

    mgr = resp.get("manager", {}).get("affected_items", [])
    if mgr:
        m = mgr[0]
        st.markdown(f"""
        <table class="inc-table">
            <thead><tr><th>Node</th><th>Version</th><th>Type</th><th>Status</th><th>OpenSSL</th></tr></thead>
            <tbody>
            <tr>
                <td class="agent-cell">{m.get('path', 'N/A')}</td>
                <td class="rule-id">{m.get('version', 'N/A')}</td>
                <td>{m.get('type', 'N/A')}</td>
                <td><span class='sev-badge sev-low'>RUNNING</span></td>
                <td>{m.get('openssl_support', 'N/A')}</td>
            </tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)

    idx = resp.get("indexer", [])
    if idx:
        st.markdown("<div class='sec-header'>Indexer Cluster</div>", unsafe_allow_html=True)
        i = idx[0]
        st.markdown(f"""
        <table class="inc-table">
            <thead><tr><th>Cluster</th><th>Status</th><th>Nodes</th><th>Shards</th><th>Active %</th></tr></thead>
            <tbody>
            <tr>
                <td class="agent-cell">{i.get('cluster', 'N/A')}</td>
                <td><span class='sev-badge sev-low'>{str(i.get('status','N/A')).upper()}</span></td>
                <td>{i.get('node.total','N/A')}</td>
                <td>{i.get('shards','N/A')}</td>
                <td>{i.get('active_shards_percent','N/A')}</td>
            </tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# HELPER: Load all alerts (separate cache for these derived pages)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner=False)
def load_all_alerts():
    resp = api_get("/api/alerts", params={"limit": 500})
    if "__error__" in resp:
        return []
    return resp.get("items", [])

# ──────────────────────────────────────────────────────────────────────────────
# PAGE: THREAT INTELLIGENCE (derived from src_ip / dst_ip in alerts)
# ──────────────────────────────────────────────────────────────────────────────
def page_threat_intel():
    render_topbar("Threat Intelligence — IOC Reputation")
    items = load_all_alerts()
    if not items:
        st.markdown("<div style='padding:2rem;color:#484F58;font-size:0.82rem;'>No alert data available.</div>", unsafe_allow_html=True)
        return

    df = pd.DataFrame(items)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    ioc_rows = []
    for _, row in df.iterrows():
        for ip_field, ioc_type in [("src_ip", "Source IP"), ("dst_ip", "Destination IP")]:
            ip = row.get(ip_field)
            if ip and str(ip) not in ("None", "", "nan"):
                ioc_rows.append({
                    "ioc": str(ip), "type": ioc_type,
                    "severity": row.get("severity", "unknown"),
                    "agent": row.get("agent_name", "Unknown"),
                    "timestamp": row["timestamp"],
                    "rule_id": row.get("rule_id", ""),
                    "desc": row.get("rule_description", ""),
                })

    if not ioc_rows:
        st.markdown("""
        <div style='padding:2rem; background:#161B22; border:1px solid #21262D; color:#484F58; font-size:0.82rem;'>
            No IP-based IOCs detected in the current alert stream.<br>
            <span style='font-size:0.72rem;'>Wazuh rules that generate src_ip/dst_ip fields will populate this view.</span>
        </div>""", unsafe_allow_html=True)
        return

    df_ioc = pd.DataFrame(ioc_rows)
    summary_df = (
        df_ioc.groupby(["ioc", "type"])
        .agg(
            hit_count=("ioc", "count"),
            severities=("severity", lambda x: sorted(set(x), key=lambda s: {"critical":0,"high":1,"medium":2,"low":3}.get(s,4))[0]),
            assets=("agent", lambda x: ", ".join(sorted(set(x))[:3])),
            first_seen=("timestamp", "min"),
            last_seen=("timestamp", "max"),
        )
        .reset_index()
        .sort_values("hit_count", ascending=False)
    )

    st.markdown(f"<div class='sec-header'>Observed IOCs — {len(summary_df)} Unique Indicators</div>", unsafe_allow_html=True)

    rows_html = ""
    for _, r in summary_df.iterrows():
        badge = sev_badge(r["severities"])
        rows_html += f"""<tr>
            <td class="agent-cell" style="font-family:'JetBrains Mono',monospace;">{r['ioc']}</td>
            <td class="rule-id">{r['type']}</td>
            <td>{badge}</td>
            <td class="rule-id">{r['hit_count']}</td>
            <td class="desc-cell">{str(r['assets'])[:50]}</td>
            <td class="ts-cell">{fmt_ts(r['first_seen'])}</td>
            <td class="ts-cell">{fmt_ts(r['last_seen'])}</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto; background:#161B22; border:1px solid #21262D;">
    <table class="evt-table">
        <thead><tr><th>IP Address</th><th>Type</th><th>Max Severity</th>
        <th>Hit Count</th><th>Affected Assets</th><th>First Seen</th><th>Last Seen</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table></div>""", unsafe_allow_html=True)

    st.markdown("<div class='sec-header'>Top 10 Most Active IOCs</div>", unsafe_allow_html=True)
    top10 = summary_df.head(10)
    fig = px.bar(top10, x="ioc", y="hit_count",
                 color="severities",
                 color_discrete_map={"critical":"#F85149","high":"#D29922","medium":"#388BFD","low":"#3FB950"},
                 labels={"ioc":"IP Address","hit_count":"Alert Count"})
    fig.update_layout(plot_bgcolor="#0D1117", paper_bgcolor="#0D1117",
                      font=dict(color="#8B949E", size=10),
                      margin=dict(l=0,r=0,t=5,b=0), height=220, showlegend=False,
                      xaxis=dict(tickangle=-30), yaxis=dict(showgrid=True, gridcolor="#161B22"))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ──────────────────────────────────────────────────────────────────────────────
# PAGE: MITRE ATT&CK (derived from mitre_techniques or rule groups)
# ──────────────────────────────────────────────────────────────────────────────
def page_mitre():
    render_topbar("MITRE ATT&CK — Technique Coverage")
    items = load_all_alerts()
    if not items:
        st.markdown("<div style='padding:2rem;color:#484F58;'>No alert data available.</div>", unsafe_allow_html=True)
        return

    tech_rows = []
    label_col = "MITRE Technique"
    for item in items:
        techs = item.get("mitre_techniques") or []
        if isinstance(techs, str):
            techs = [t.strip() for t in techs.split(",") if t.strip()]
        for tech in techs:
            tech_rows.append({
                "technique": str(tech),
                "severity": item.get("severity", "unknown"),
                "agent": item.get("agent_name", "Unknown"),
                "rule_id": item.get("rule_id", ""),
                "desc": item.get("rule_description", ""),
            })

    # Fallback: use Wazuh rule groups if no MITRE IDs
    if not tech_rows:
        label_col = "Wazuh Rule Group (MITRE Proxy)"
        for item in items:
            groups = item.get("groups") or []
            if isinstance(groups, str):
                groups = [groups]
            for g in groups:
                if g:
                    tech_rows.append({
                        "technique": g,
                        "severity": item.get("severity", "unknown"),
                        "agent": item.get("agent_name", "Unknown"),
                        "rule_id": item.get("rule_id", ""),
                        "desc": item.get("rule_description", ""),
                    })

    if not tech_rows:
        st.markdown("""
        <div style='padding:2rem; background:#161B22; border:1px solid #21262D; color:#484F58; font-size:0.82rem;'>
            No MITRE technique tags in current alerts.<br>
            <span style='font-size:0.72rem;'>Wazuh rules with <code>rule.mitre.id</code> fields will populate this view.</span>
        </div>""", unsafe_allow_html=True)
        return

    df_t = pd.DataFrame(tech_rows)
    summary = (
        df_t.groupby("technique")
        .agg(
            count=("technique", "count"),
            top_sev=("severity", lambda x: sorted(set(x), key=lambda s: {"critical":0,"high":1,"medium":2,"low":3}.get(s,4))[0]),
            assets=("agent", lambda x: len(set(x))),
            rules=("rule_id", lambda x: ", ".join(sorted(set(str(r) for r in x))[:3])),
            sample_desc=("desc", "first"),
        )
        .reset_index()
        .sort_values("count", ascending=False)
    )

    st.markdown(f"<div class='sec-header'>{label_col} — {len(summary)} Techniques Observed</div>", unsafe_allow_html=True)

    rows_html = ""
    for _, r in summary.iterrows():
        badge = sev_badge(r["top_sev"])
        rows_html += f"""<tr>
            <td class="agent-cell" style="font-family:'JetBrains Mono',monospace;">{r['technique']}</td>
            <td>{badge}</td>
            <td class="rule-id">{r['count']}</td>
            <td class="rule-id">{r['assets']}</td>
            <td class="rule-id">{str(r['rules'])[:50]}</td>
            <td class="desc-cell">{str(r['sample_desc'])[:60]}</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto; background:#161B22; border:1px solid #21262D;">
    <table class="evt-table">
        <thead><tr><th>{label_col}</th><th>Max Severity</th>
        <th>Alert Count</th><th>Assets</th><th>Rules</th><th>Sample Description</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table></div>""", unsafe_allow_html=True)

    st.markdown("<div class='sec-header'>Technique Frequency Chart</div>", unsafe_allow_html=True)
    top = summary.head(15).iloc[::-1]
    fig = px.bar(top, x="count", y="technique", orientation="h",
                 color="top_sev",
                 color_discrete_map={"critical":"#F85149","high":"#D29922","medium":"#388BFD","low":"#3FB950"},
                 labels={"technique":"","count":"Alert Count"})
    fig.update_layout(plot_bgcolor="#0D1117", paper_bgcolor="#0D1117",
                      font=dict(color="#8B949E", size=10),
                      margin=dict(l=0,r=0,t=5,b=0), height=max(250, len(top)*26),
                      xaxis=dict(showgrid=True, gridcolor="#161B22"),
                      yaxis=dict(showgrid=False), showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ──────────────────────────────────────────────────────────────────────────────
# PAGE: DETECTION RULES (derived from rule_id in alerts)
# ──────────────────────────────────────────────────────────────────────────────
def page_rules():
    render_topbar("Detection Rules — Active Rule Inventory")
    items = load_all_alerts()
    if not items:
        st.markdown("<div style='padding:2rem;color:#484F58;'>No alert data available.</div>", unsafe_allow_html=True)
        return

    df = pd.DataFrame(items)
    rules = (
        df.groupby(["rule_id", "rule_description", "severity"])
        .agg(count=("id", "count"))
        .reset_index()
        .sort_values("count", ascending=False)
        .drop_duplicates(subset=["rule_id"])
    )

    st.markdown(f"<div class='sec-header'>Active Detection Rules — {len(rules)} Rules Firing</div>", unsafe_allow_html=True)

    rows_html = ""
    for _, r in rules.iterrows():
        badge = sev_badge(r["severity"])
        rows_html += f"""<tr>
            <td class="rule-id" style="font-family:'JetBrains Mono',monospace;">{r['rule_id']}</td>
            <td>{badge}</td>
            <td class="desc-cell">{str(r['rule_description'])[:80]}</td>
            <td class="rule-id">{r['count']}</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto; background:#161B22; border:1px solid #21262D;">
    <table class="evt-table">
        <thead><tr><th>Rule ID</th><th>Severity</th><th>Description</th><th>Trigger Count</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table></div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# PAGE: ASSETS (derived from agent fields in alerts)
# ──────────────────────────────────────────────────────────────────────────────
def page_assets():
    render_topbar("Asset Inventory — Monitored Endpoints")
    items = load_all_alerts()
    if not items:
        st.markdown("<div style='padding:2rem;color:#484F58;'>No alert data available.</div>", unsafe_allow_html=True)
        return

    df = pd.DataFrame(items)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    agg_dict = {
        "alert_count": ("id", "count"),
        "last_seen": ("timestamp", "max"),
        "first_seen": ("timestamp", "min"),
        "critical": ("severity", lambda x: (x == "critical").sum()),
        "high": ("severity", lambda x: (x == "high").sum()),
    }
    if "agent_ip" in df.columns:
        agg_dict["agent_ip"] = ("agent_ip", "first")

    assets = (
        df.groupby("agent_name")
        .agg(**agg_dict)
        .reset_index()
        .sort_values("alert_count", ascending=False)
    )

    st.markdown(f"<div class='sec-header'>Monitored Assets — {len(assets)} Endpoints Reporting</div>", unsafe_allow_html=True)

    rows_html = ""
    for _, r in assets.iterrows():
        risk = "critical" if r["critical"] > 0 else ("high" if r["high"] > 0 else "low")
        badge = sev_badge(risk)
        ip = str(r.get("agent_ip", "—")) if "agent_ip" in r else "—"
        rows_html += f"""<tr>
            <td class="agent-cell">{r['agent_name']}</td>
            <td class="ip-cell">{ip}</td>
            <td>{badge}</td>
            <td class="rule-id">{r['alert_count']}</td>
            <td class="rule-id" style="color:#F85149;">{int(r['critical'])}</td>
            <td class="rule-id" style="color:#D29922;">{int(r['high'])}</td>
            <td class="ts-cell">{fmt_ts(r['first_seen'])}</td>
            <td class="ts-cell">{fmt_ts(r['last_seen'])}</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto; background:#161B22; border:1px solid #21262D;">
    <table class="inc-table">
        <thead><tr><th>Hostname</th><th>IP</th><th>Risk</th><th>Total Alerts</th>
        <th>Critical</th><th>High</th><th>First Seen</th><th>Last Seen</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table></div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# PAGE: REPORTS
# ──────────────────────────────────────────────────────────────────────────────
def page_reports():
    render_topbar("Reports & Analytics")
    summary = api_get("/api/dashboard/summary")
    if "__error__" in summary:
        st.error("Could not load summary data.")
        return

    st.markdown("<div class='sec-header'>Platform Activity Summary</div>", unsafe_allow_html=True)
    items = load_all_alerts()
    sev = summary.get("severity_counts", {})
    report_data = {
        "report_generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "platform": "SentinelIQ Enterprise SIEM",
        "metrics": {
            "total_events": summary.get("alert_count", 0),
            "severity_breakdown": sev,
            "open_incidents": summary.get("open_incident_count", 0),
        },
    }
    if items:
        df = pd.DataFrame(items)
        report_data["top_10_firing_rules"] = df.groupby("rule_id").size().sort_values(ascending=False).head(10).to_dict()
        report_data["alert_count_by_asset"] = df.groupby("agent_name").size().sort_values(ascending=False).to_dict()

    col1, col2 = st.columns([2, 1])
    with col1:
        st.json(report_data)
    with col2:
        st.download_button(
            "Download Full Report (JSON)",
            data=json.dumps(report_data, indent=2, default=str),
            file_name=f"SentinelIQ_Report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
        )


# ──────────────────────────────────────────────────────────────────────────────
# MAIN ROUTER
# ──────────────────────────────────────────────────────────────────────────────
def main():
    render_sidebar()
    page = st.session_state.nav

    if page == "Overview":              page_overview()
    elif page == "Security Events":     page_security_events()
    elif page == "Incidents":           page_incidents()
    elif page == "Threat Intelligence": page_threat_intel()
    elif page == "MITRE ATT&CK":        page_mitre()
    elif page == "Detection Rules":     page_rules()
    elif page == "Assets":              page_assets()
    elif page == "Agents":              page_agents()
    elif page == "Reports":             page_reports()

main()
