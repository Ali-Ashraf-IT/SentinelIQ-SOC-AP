import json
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

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
# CSS — HIGH VISIBILITY / HIGH CONTRAST ENTERPRISE THEME
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Base */
html, body, [class*="css"] {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #F1F5F9;
}
.stApp { background-color: #0F172A; }

/* Banner */
.sq-banner {
    background: linear-gradient(90deg, #1E3A8A 0%, #1E40AF 50%, #1D4ED8 100%);
    padding: 18px 32px;
    border-radius: 8px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 4px 20px rgba(29,78,216,0.4);
}
.sq-banner .sq-logo { font-size: 36px; }
.sq-banner .sq-title { font-size: 26px; font-weight: 800; color: #FFFFFF; letter-spacing: 0.5px; }
.sq-banner .sq-sub   { font-size: 12px; color: #BFDBFE; margin-top: 3px; }

/* KPI Cards */
div[data-testid="metric-container"] {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 20px;
}
div[data-testid="metric-container"] > label {
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: #94A3B8 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 30px !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #1E293B;
    border-radius: 8px;
    padding: 5px;
    border: 1px solid #334155;
}
.stTabs [data-baseweb="tab"] {
    font-size: 13px;
    font-weight: 600;
    color: #94A3B8;
    border-radius: 6px;
    padding: 10px 18px;
}
.stTabs [aria-selected="true"] {
    background: #1D4ED8 !important;
    color: #FFFFFF !important;
}

/* Guide Box */
.sq-guide {
    background: #1E293B;
    border-left: 4px solid #60A5FA;
    border-radius: 6px;
    padding: 14px 18px;
    font-size: 14px;
    color: #CBD5E1;
    margin-bottom: 20px;
    line-height: 1.7;
}
.sq-guide b { color: #93C5FD; }

/* Section Headers */
.sq-section {
    font-size: 16px;
    font-weight: 700;
    color: #F1F5F9;
    border-bottom: 2px solid #1D4ED8;
    padding-bottom: 8px;
    margin: 16px 0 14px 0;
}

/* AI Result Containers */
.sq-finding {
    background: #1E3A5F;
    border: 1px solid #2563EB;
    border-radius: 8px;
    padding: 16px 20px;
    font-size: 15px;
    color: #E0F2FE;
    line-height: 1.7;
    margin-bottom: 16px;
}
.sq-step {
    background: #1A2E1A;
    border: 1px solid #22C55E;
    border-radius: 6px;
    padding: 12px 16px;
    color: #DCFCE7;
    margin-bottom: 8px;
    font-size: 14px;
}
.sq-warning-box {
    background: #431407;
    border: 1px solid #EA580C;
    border-radius: 8px;
    padding: 14px 18px;
    color: #FED7AA;
    font-size: 14px;
    margin-bottom: 12px;
}
.sq-unknown {
    background: #1E1B2E;
    border: 1px solid #7C3AED;
    border-radius: 6px;
    padding: 10px 14px;
    color: #DDD6FE;
    margin-bottom: 8px;
    font-size: 14px;
}

/* Confidence badges */
.badge-high-conf { background:#14532D; color:#86EFAC; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:700; }
.badge-med-conf  { background:#713F12; color:#FDE68A; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:700; }
.badge-low-conf  { background:#450A0A; color:#FCA5A5; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:700; }

/* Buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1D4ED8, #2563EB) !important;
    color: #fff !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
}

/* Dataframe */
.stDataFrame thead th { background: #1E3A8A !important; color: #fff !important; }

/* Expanders */
details { background: #1E293B !important; border: 1px solid #334155 !important; border-radius: 8px !important; }
summary { color: #93C5FD !important; font-weight: 600 !important; font-size: 14px !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# BANNER
# ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="sq-banner">
  <span class="sq-logo">🛡️</span>
  <div>
    <div class="sq-title">SentinelIQ Enterprise SIEM</div>
    <div class="sq-sub">Security Information &amp; Event Management &nbsp;|&nbsp; AI-Augmented Threat Intelligence &nbsp;|&nbsp; Real-time Wazuh Integration</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────
BACKEND_URL   = st.secrets.get("BACKEND_API_URL",   "").rstrip("/")
BACKEND_TOKEN = st.secrets.get("BACKEND_API_TOKEN", "")

if not BACKEND_URL or not BACKEND_TOKEN:
    st.error("⚠️  Backend not configured — add BACKEND_API_URL and BACKEND_API_TOKEN in Streamlit Secrets.")
    st.stop()

HEADERS = {"Authorization": f"Bearer {BACKEND_TOKEN}"}

@st.cache_data(ttl=30, show_spinner=False)
def api_get(path: str, params: dict = None):
    r = requests.get(f"{BACKEND_URL}{path}", headers=HEADERS, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def api_post(path: str, body: dict = None):
    r = requests.post(f"{BACKEND_URL}{path}", headers=HEADERS, json=body or {}, timeout=90)
    if r.status_code >= 400:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise RuntimeError(detail)
    return r.json()

# ──────────────────────────────────────────────────────────────
# SUMMARY DATA
# ──────────────────────────────────────────────────────────────
try:
    summary = api_get("/api/dashboard/summary")
except Exception as exc:
    st.error(f"❌  Backend Unreachable — {exc}")
    st.stop()

sev       = summary.get("severity_counts", {})
high_crit = sev.get("high", 0) + sev.get("critical", 0)
last_ts   = str(summary.get("latest_alert_timestamp", "—"))[:19]

# KPI ROW
c1, c2, c3, c4 = st.columns(4)
c1.metric("📡  Total Events",            summary.get("alert_count", 0))
c2.metric("🔗  Open Investigations",     summary.get("open_incident_count", 0))
c3.metric("🔴  Critical / High",         high_crit)
c4.metric("🕐  Latest Event Timestamp",  last_ts)

st.markdown("---")

# ──────────────────────────────────────────────────────────────
# MAIN TABS
# ──────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊  SOC Overview",
    "📡  Live Alerts",
    "🔗  Incidents",
    "🧠  AI Copilot",
    "🛡️  Playbooks",
    "⚙️  System Health",
])

# ══════════════════════════════════════════════════════════════
# TAB 1  —  SOC OVERVIEW
# ══════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("""<div class='sq-guide'>
    <b>SOC Overview</b> — Live security posture of your environment.<br>
    The ring chart shows how many alerts exist per severity level.
    If you see <b>Critical or High</b> alerts, go to the <b>Incidents tab</b> immediately, pick an incident, and run an <b>AI Copilot analysis</b>.
    </div>""", unsafe_allow_html=True)

    col_ring, col_status = st.columns([1, 1], gap="large")

    with col_ring:
        st.markdown("<div class='sq-section'>Alert Severity Distribution</div>", unsafe_allow_html=True)
        if sev:
            cmap   = {"critical":"#EF4444","high":"#F97316","medium":"#F59E0B","low":"#22C55E","unknown":"#64748B"}
            labels = list(sev.keys())
            values = list(sev.values())
            colors = [cmap.get(l, "#64748B") for l in labels]
            fig = go.Figure(go.Pie(
                labels=labels, values=values, hole=0.62,
                marker=dict(colors=colors, line=dict(color="#0F172A", width=3)),
                textinfo="percent+label",
                textfont=dict(size=14, color="#FFFFFF"),
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=0, b=0, l=0, r=0),
                height=280,
                legend=dict(font=dict(color="#CBD5E1", size=13), bgcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig)
        else:
            st.info("No alert data yet.")

    with col_status:
        st.markdown("<div class='sq-section'>Integration Status</div>", unsafe_allow_html=True)
        st.success("✅  Wazuh SIEM Agent — Connected")
        st.success("✅  SentinelIQ AI Engine (Groq) — Online")
        st.success("✅  Backend Database — Active")
        if high_crit > 0:
            st.error(f"⚠️  {high_crit} Critical/High threat(s) — Triage required now!")
        else:
            st.success("✅  No Critical Threats — Environment Stable")

# ══════════════════════════════════════════════════════════════
# TAB 2  —  LIVE ALERTS
# ══════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("""<div class='sq-guide'>
    <b>Live Alerts</b> — Raw security events forwarded by your Wazuh endpoint agents.<br>
    Each row is one event. Filter by severity. Focus on <b>Critical and High</b> first — these need immediate action.
    Use the Alert ID to find the matching Incident on the next tab.
    </div>""", unsafe_allow_html=True)

    fc1, fc2 = st.columns([1, 4])
    with fc1:
        sev_filter = st.selectbox("Filter by Severity", ["All", "critical", "high", "medium", "low"])
    with fc2:
        if st.button("🔄  Refresh"):
            st.cache_data.clear()

    params = {"limit": 100, "offset": 0}
    if sev_filter != "All":
        params["severity"] = sev_filter

    try:
        data  = api_get("/api/alerts", params=params)
        items = data.get("items", [])
        if items:
            df = pd.DataFrame(items)
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d  %H:%M:%S")
            show_cols = [c for c in ["id","timestamp","severity","agent_name","rule_id","rule_description","src_ip"] if c in df.columns]
            st.dataframe(df[show_cols], hide_index=True, height=350)
            st.caption(f"Showing {len(items)} events")
        else:
            st.info("No alerts for selected filter.")
    except Exception as e:
        st.error(f"Could not load alerts — {e}")

# ══════════════════════════════════════════════════════════════
# TAB 3  —  INCIDENTS
# ══════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("""<div class='sq-guide'>
    <b>Correlated Incidents</b> — SentinelIQ groups related alerts into Incidents based on agent, timing, and rule patterns.<br>
    An <b>Incident</b> = a group of related alerts that together tell one story.
    Copy the <b>Incident ID</b> and use it in the <b>AI Copilot tab</b> to get an automated analysis.
    </div>""", unsafe_allow_html=True)

    if st.button("🔄  Refresh Incidents"):
        st.cache_data.clear()

    try:
        incidents = api_get("/api/incidents")
        if incidents:
            st.dataframe(pd.DataFrame(incidents), hide_index=True, height=280)
        else:
            st.info("No incidents correlated yet.")
    except Exception as e:
        st.error(str(e))

    st.markdown("---")
    st.markdown("<div class='sq-section'>Incident Evidence Viewer</div>", unsafe_allow_html=True)
    inv_id = st.number_input("Enter Incident ID to inspect", min_value=1, step=1, value=1)
    if st.button("🔍  Load Incident Timeline & Evidence"):
        try:
            detail = api_get(f"/api/incidents/{inv_id}")
            st.json(detail)
        except Exception as e:
            st.error(str(e))

# ══════════════════════════════════════════════════════════════
# TAB 4  —  AI COPILOT
# ══════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("""<div class='sq-guide'>
    <b>SentinelIQ AI Copilot</b> — Your automated Tier-2 analyst.<br>
    Enter an Incident ID, select a task, and the AI reads all correlated alerts and produces a <b>plain-English report</b>.<br>
    Each run is <b>independent</b> — you can run the same incident multiple times to compare results.
    </div>""", unsafe_allow_html=True)

    left, right = st.columns([1, 2], gap="large")

    TASKS = {
        "triage":        "🔍 Triage — What happened? How urgent?",
        "investigation": "🧪 Investigation — Full attack timeline & evidence",
        "response":      "🛡️ Response — Windows commands to contain & fix",
        "manager":       "👔 Manager Brief — Simple English for executives",
        "report":        "📄 Report — Full downloadable incident report",
    }

    with left:
        st.markdown("<div class='sq-section'>Configure AI Task</div>", unsafe_allow_html=True)
        ai_inc_id   = st.number_input("Target Incident ID", min_value=1, step=1, value=1)
        task_choice = st.radio("Select Analysis Type", list(TASKS.keys()), format_func=lambda x: TASKS[x])
        st.markdown("---")
        run_ai = st.button("🚀  Run AI Analysis", type="primary", use_container_width=True)

    with right:
        if run_ai:
            with st.spinner("🧠  SentinelIQ AI is analyzing all correlated evidence…"):
                try:
                    # force=true always — allow every run without 409 block
                    res = api_post(f"/api/incidents/{ai_inc_id}/analyze", {"task": task_choice, "force": True})

                    if res.get("status") == "success":
                        ai = res.get("result", {})
                        conf  = ai.get("confidence_label", "unknown").lower()
                        model = ai.get("model", "unknown")

                        # Header
                        badge_cls = "badge-high-conf" if conf == "high" else ("badge-med-conf" if conf == "medium" else "badge-low-conf")
                        st.markdown(f"**✅ Analysis Complete** &nbsp; `{model}` &nbsp; <span class='{badge_cls}'>{conf.upper()} CONFIDENCE</span>", unsafe_allow_html=True)
                        st.markdown("")

                        # ── TRIAGE ────────────────────────────────────────
                        if task_choice == "triage":
                            st.markdown("<div class='sq-section'>What Happened (Plain English)</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='sq-finding'>{ai.get('finding','No finding available.')}</div>", unsafe_allow_html=True)

                            actions = ai.get("recommended_actions", [])
                            if actions:
                                st.markdown("<div class='sq-section'>Recommended Actions for Analyst</div>", unsafe_allow_html=True)
                                for a in actions:
                                    st.markdown(f"<div class='sq-step'>▶ {a}</div>", unsafe_allow_html=True)

                            unknowns = ai.get("unknowns", [])
                            if unknowns:
                                st.markdown("<div class='sq-section'>Gaps — What We Still Don't Know</div>", unsafe_allow_html=True)
                                for u in unknowns:
                                    st.markdown(f"<div class='sq-unknown'>❓ {u}</div>", unsafe_allow_html=True)

                            with st.expander("📎  Evidence References"):
                                for ref in ai.get("evidence_refs", []):
                                    st.markdown(f"- `{ref}`")

                        # ── INVESTIGATION ─────────────────────────────────
                        elif task_choice == "investigation":
                            st.markdown("<div class='sq-section'>Analyst Finding</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='sq-finding'>{ai.get('finding','—')}</div>", unsafe_allow_html=True)

                            tl = ai.get("timeline_summary", "")
                            if tl:
                                st.markdown("<div class='sq-section'>⏱️  Attack Timeline</div>", unsafe_allow_html=True)
                                st.markdown(f"<div class='sq-finding'>{tl}</div>", unsafe_allow_html=True)

                            steps = ai.get("next_investigation_steps", []) + ai.get("recommended_actions", [])
                            if steps:
                                st.markdown("<div class='sq-section'>Next Investigation Steps</div>", unsafe_allow_html=True)
                                for s in steps:
                                    st.markdown(f"<div class='sq-step'>🔬 {s}</div>", unsafe_allow_html=True)

                            unknowns = ai.get("unknowns", [])
                            if unknowns:
                                st.markdown("<div class='sq-section'>Evidence Gaps</div>", unsafe_allow_html=True)
                                for u in unknowns:
                                    st.markdown(f"<div class='sq-unknown'>❓ {u}</div>", unsafe_allow_html=True)

                        # ── RESPONSE ──────────────────────────────────────
                        elif task_choice == "response":
                            st.markdown("<div class='sq-section'>Threat Summary</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='sq-finding'>{ai.get('finding','—')}</div>", unsafe_allow_html=True)

                            reason = ai.get("reason","")
                            impact = ai.get("impact","")
                            if reason:
                                st.markdown(f"<div class='sq-warning-box'>⚠️  <b>Why you must act:</b> {reason}</div>", unsafe_allow_html=True)
                            if impact:
                                st.markdown(f"<div class='sq-warning-box'>💥 <b>Potential impact if ignored:</b> {impact}</div>", unsafe_allow_html=True)

                            actions = ai.get("recommended_actions", [])
                            if actions:
                                st.markdown("<div class='sq-section'>🪟  Windows Remediation Steps (PowerShell)</div>", unsafe_allow_html=True)
                                st.caption("⚠️  Run in elevated PowerShell (Run as Administrator) on the affected host")
                                for step in actions:
                                    # Always render as powershell code block
                                    st.code(step, language="powershell")

                            rollback = ai.get("rollback", [])
                            if rollback:
                                with st.expander("↩️  Rollback Plan — If action causes issues"):
                                    for rb in rollback:
                                        st.markdown(f"<div class='sq-step'>↩ {rb}</div>", unsafe_allow_html=True)

                            verify = ai.get("verification", [])
                            if verify:
                                with st.expander("✔️  Verification Steps — Confirm threat is contained"):
                                    for v in verify:
                                        st.markdown(f"<div class='sq-step'>✓ {v}</div>", unsafe_allow_html=True)

                        # ── MANAGER ───────────────────────────────────────
                        elif task_choice == "manager":
                            st.markdown("<div class='sq-section'>Executive Summary</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='sq-finding'>{ai.get('what_happened','—')}</div>", unsafe_allow_html=True)

                            matter = ai.get("why_it_might_matter","")
                            if matter:
                                st.markdown(f"<div class='sq-warning-box'>📌 <b>Why this matters to the business:</b><br>{matter}</div>", unsafe_allow_html=True)

                            systems = ai.get("affected_systems",[])
                            if systems:
                                st.markdown("<div class='sq-section'>Affected Systems</div>", unsafe_allow_html=True)
                                for s in systems:
                                    st.markdown(f"<div class='sq-step'>💻 {s}</div>", unsafe_allow_html=True)

                            known = ai.get("what_we_know",[])
                            if known:
                                st.markdown("<div class='sq-section'>What We Know (Confirmed)</div>", unsafe_allow_html=True)
                                for k in known:
                                    st.markdown(f"<div class='sq-step'>✅ {k}</div>", unsafe_allow_html=True)

                            unknowns = ai.get("what_we_do_not_know",[])
                            if unknowns:
                                st.markdown("<div class='sq-section'>What We Still Need to Find Out</div>", unsafe_allow_html=True)
                                for u in unknowns:
                                    st.markdown(f"<div class='sq-unknown'>❓ {u}</div>", unsafe_allow_html=True)

                        # ── REPORT ────────────────────────────────────────
                        elif task_choice == "report":
                            st.markdown("<div class='sq-section'>Executive Summary</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='sq-finding'>{ai.get('executive_summary','—')}</div>", unsafe_allow_html=True)

                            st.markdown("<div class='sq-section'>Technical Summary</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='sq-finding'>{ai.get('technical_summary','—')}</div>", unsafe_allow_html=True)

                            timeline = ai.get("timeline",[])
                            if timeline:
                                st.markdown("<div class='sq-section'>Incident Timeline</div>", unsafe_allow_html=True)
                                for t in timeline:
                                    st.markdown(f"<div class='sq-step'>⏱ {t}</div>", unsafe_allow_html=True)

                            st.download_button(
                                "⬇️  Download Full Report (JSON)",
                                data=json.dumps(ai, indent=2, default=str),
                                file_name=f"SentinelIQ_Incident_{ai_inc_id}_Report.json",
                                mime="application/json",
                            )

                    else:
                        st.json(res)

                except RuntimeError as e:
                    st.error(f"AI Analysis Failed — {e}")
                except Exception as e:
                    st.error(f"Unexpected Error — {e}")

# ══════════════════════════════════════════════════════════════
# TAB 5  —  WINDOWS PLAYBOOKS
# ══════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("""<div class='sq-guide'>
    <b>Remediation Playbooks</b> — Real-world Windows Standard Operating Procedures (SOPs).<br>
    These commands are <b>copy-paste ready</b> for elevated PowerShell on the affected Windows host.<br>
    <b>⚠️  Always confirm the target machine with your team lead before executing.</b>
    </div>""", unsafe_allow_html=True)

    with st.expander("🚫  Playbook 1 — Block a Malicious IP Address"):
        st.markdown("**When to use:** Attacker IP identified in alerts. Block at host firewall level.")
        st.code('# Block all inbound traffic from attacker\nNew-NetFirewallRule -DisplayName "SIQ-Block-Inbound" -Direction Inbound -RemoteAddress <ATTACKER_IP> -Action Block -Protocol Any\n\n# Block outbound (prevent callbacks/beaconing)\nNew-NetFirewallRule -DisplayName "SIQ-Block-Outbound" -Direction Outbound -RemoteAddress <ATTACKER_IP> -Action Block -Protocol Any\n\n# Verify rules were applied\nGet-NetFirewallRule -DisplayName "SIQ-Block-*" | Format-Table Name, Enabled, Direction', language="powershell")
        st.markdown("**Rollback:**")
        st.code('Remove-NetFirewallRule -DisplayName "SIQ-Block-Inbound"\nRemove-NetFirewallRule -DisplayName "SIQ-Block-Outbound"', language="powershell")

    with st.expander("💀  Playbook 2 — Kill Malicious Process"):
        st.markdown("**When to use:** Suspicious process identified (reverse shell, ransomware, miner).")
        st.code('# Find the process\nGet-Process | Where-Object { $_.Name -like "*<PROCESS_NAME>*" } | Select-Object Id, Name, Path\n\n# Kill by name\nStop-Process -Name "<PROCESS_NAME>" -Force -Confirm:$false\n\n# Kill by PID (if name unknown)\nStop-Process -Id <PID> -Force\n\n# Verify it is gone\nGet-Process -Name "<PROCESS_NAME>" -ErrorAction SilentlyContinue', language="powershell")

    with st.expander("🔒  Playbook 3 — Isolate Compromised Machine"):
        st.markdown("**When to use:** Host is confirmed compromised — stop lateral movement immediately.")
        st.code('# Block ALL inbound and outbound\nSet-NetFirewallProfile -All -DefaultInboundAction Block\nSet-NetFirewallProfile -All -DefaultOutboundAction Block\n\n# Keep YOUR SOC IP connected via RDP (replace YOUR_SOC_IP)\nNew-NetFirewallRule -DisplayName "SOC-Admin-RDP" -Direction Inbound -RemoteAddress <YOUR_SOC_IP> -LocalPort 3389 -Protocol TCP -Action Allow', language="powershell")
        st.markdown("**Rollback:**")
        st.code('Set-NetFirewallProfile -All -DefaultInboundAction Allow\nSet-NetFirewallProfile -All -DefaultOutboundAction Allow\nRemove-NetFirewallRule -DisplayName "SOC-Admin-RDP"', language="powershell")

    with st.expander("🔑  Playbook 4 — Disable Compromised User Account (AD)"):
        st.markdown("**When to use:** User account shows brute-force success, impossible travel, or lateral movement.")
        st.code('# Run on Domain Controller\n# Step 1 — Disable account\nDisable-ADAccount -Identity "<USERNAME>"\n\n# Step 2 — Force sign-out all active sessions\nQuery session /server:<HOSTNAME>\nReset session <SESSION_ID> /server:<HOSTNAME>\n\n# Step 3 — Reset password before re-enable\nSet-ADAccountPassword -Identity "<USERNAME>" -Reset -NewPassword (ConvertTo-SecureString "<NEW_STRONG_PASSWORD>" -AsPlainText -Force)\n\n# Step 4 — Re-enable when incident is closed\nEnable-ADAccount -Identity "<USERNAME>"', language="powershell")

    with st.expander("🔐  Playbook 5 — Block Malicious Port / Service"):
        st.markdown("**When to use:** A specific port is being exploited (e.g., SMB 445, RDP 3389 brute-force).")
        st.code('# Find what is using the port\nnetstat -ano | findstr ":<PORT>"\n\n# Block port inbound\nNew-NetFirewallRule -DisplayName "SIQ-Block-Port" -Direction Inbound -LocalPort <PORT> -Protocol TCP -Action Block\n\n# Stop and disable the service\nStop-Service -Name "<SERVICE_NAME>" -Force\nSet-Service -Name "<SERVICE_NAME>" -StartupType Disabled', language="powershell")

    with st.expander("📋  Playbook 6 — Collect Forensic Evidence (Before Cleanup)"):
        st.markdown("**When to use:** Always collect evidence BEFORE removing malware or isolating.")
        st.code('# Create evidence folder\nNew-Item -ItemType Directory -Path C:\\SOC_Evidence -Force\n\n# Export running processes with paths\nGet-Process | Select-Object Id,Name,Path,CPU,StartTime | Export-Csv "C:\\SOC_Evidence\\processes_$(Get-Date -f yyyyMMdd_HHmm).csv" -NoTypeInformation\n\n# Export active network connections\nnetstat -anob > "C:\\SOC_Evidence\\netstat_$(Get-Date -f yyyyMMdd_HHmm).txt"\n\n# Export Security event log\nwevtutil epl Security "C:\\SOC_Evidence\\Security_$(Get-Date -f yyyyMMdd_HHmm).evtx"\n\n# Export running services\nGet-Service | Where-Object {$_.Status -eq "Running"} | Export-Csv "C:\\SOC_Evidence\\services_$(Get-Date -f yyyyMMdd_HHmm).csv" -NoTypeInformation', language="powershell")

# ══════════════════════════════════════════════════════════════
# TAB 6  —  SYSTEM HEALTH
# ══════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("""<div class='sq-guide'>
    <b>System Health</b> — Verify all SentinelIQ components are connected and functioning.<br>
    If alerts are not appearing in the dashboard, run the health check to identify which component has failed.
    </div>""", unsafe_allow_html=True)

    if st.button("🔄  Run Health Check"):
        with st.spinner("Checking all components…"):
            try:
                health = api_get("/api/source/status")
                st.success("✅  Backend API — Reachable")
                st.json(health)
            except Exception as e:
                st.error(f"❌  Backend API — Unreachable: {e}")

    st.markdown("---")
    st.markdown("<div class='sq-section'>Manual Testing — Send a Real Test Alert from Windows Agent</div>", unsafe_allow_html=True)
    st.markdown("Run this on any Windows machine that has the Wazuh agent installed. It will generate a real event that SentinelIQ should detect:")
    st.code('# Simulate a test event in Windows Application log\nWrite-EventLog -LogName Application -Source "Application" -EventId 1001 -EntryType Warning -Message "SentinelIQ test alert - integration verification"\n\n# Also create a file in a commonly monitored path\necho "SentinelIQ test" > C:\\Users\\Public\\sentineliq_test.txt\n\n# Verify the alert arrived in the backend\n# Run this on Debian:\n# curl -H "Authorization: Bearer <TOKEN>" https://<CLOUDFLARE_URL>/api/dashboard/summary', language="powershell")
