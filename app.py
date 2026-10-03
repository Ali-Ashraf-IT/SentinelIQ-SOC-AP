import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# ─────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="SentinelIQ Enterprise SIEM",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────
# ENTERPRISE CSS — Clean, Dark, IBM-QRadar / Sentinel inspired
# ─────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
}
.stApp { background-color: #0B0F19; }

/* ── Top Banner ── */
.sentinel-banner {
    display: flex;
    align-items: center;
    gap: 14px;
    background: linear-gradient(135deg, #111827 60%, #0F172A);
    border-bottom: 2px solid #1D4ED8;
    padding: 14px 28px;
    border-radius: 0 0 8px 8px;
    margin-bottom: 20px;
}
.sentinel-banner .logo { font-size: 32px; }
.sentinel-banner .title { font-size: 22px; font-weight: 700; color: #60A5FA; letter-spacing: .5px; }
.sentinel-banner .sub   { font-size: 12px; color: #6B7280; margin-top: 2px; }

/* ── KPI Cards ── */
div[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 18px 20px;
}
div[data-testid="metric-container"] > label {
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #6B7280 !important;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: 700;
    color: #F9FAFB !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #111827;
    border-radius: 8px;
    padding: 4px;
    gap: 2px;
    border: 1px solid #1E293B;
    margin-bottom: 16px;
}
.stTabs [data-baseweb="tab"] {
    padding: 9px 18px;
    font-size: 13px;
    font-weight: 600;
    color: #9CA3AF;
    border-radius: 6px;
}
.stTabs [aria-selected="true"] {
    background: #1D4ED8 !important;
    color: #fff !important;
}

/* ── Guide Box ── */
.guide-box {
    background: #0F172A;
    border-left: 3px solid #3B82F6;
    border-radius: 4px;
    padding: 12px 16px;
    font-size: 13px;
    color: #94A3B8;
    margin-bottom: 18px;
    line-height: 1.6;
}
.guide-box b { color: #60A5FA; }

/* ── Section headers ── */
.section-title {
    font-size: 15px;
    font-weight: 700;
    color: #E2E8F0;
    border-bottom: 1px solid #1E293B;
    padding-bottom: 6px;
    margin-bottom: 12px;
    margin-top: 8px;
}

/* ── Severity Badge ── */
.badge-critical { background:#7F1D1D; color:#FCA5A5; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700;}
.badge-high     { background:#7C2D12; color:#FED7AA; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700;}
.badge-medium   { background:#713F12; color:#FDE68A; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700;}
.badge-low      { background:#14532D; color:#86EFAC; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700;}

/* ── Buttons ── */
.stButton > button[kind="primary"] {
    background: #1D4ED8;
    color: #fff;
    border: none;
    font-weight: 600;
    border-radius: 6px;
}
.stButton > button[kind="primary"]:hover { background: #1E40AF; }

/* ── Code blocks ── */
.stCode, pre { border-radius: 6px !important; }

/* Dataframe */
.stDataFrame { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# BANNER
# ─────────────────────────────────────────────────────
st.markdown("""
<div class="sentinel-banner">
  <span class="logo">🛡️</span>
  <div>
    <div class="title">SentinelIQ Enterprise SIEM</div>
    <div class="sub">Security Information &amp; Event Management · AI-Augmented Threat Intelligence · Real-time Wazuh Integration</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# CONFIG / API HELPERS
# ─────────────────────────────────────────────────────
BACKEND_URL   = st.secrets.get("BACKEND_API_URL",   "").rstrip("/")
BACKEND_TOKEN = st.secrets.get("BACKEND_API_TOKEN", "")

if not BACKEND_URL or not BACKEND_TOKEN:
    st.error("⚠️  Backend not configured.  Add **BACKEND_API_URL** and **BACKEND_API_TOKEN** in Streamlit → Secrets.")
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

# ─────────────────────────────────────────────────────
# DASHBOARD SUMMARY
# ─────────────────────────────────────────────────────
try:
    summary = api_get("/api/dashboard/summary")
except Exception as exc:
    st.error(f"❌ Backend Server Unavailable — {exc}")
    st.stop()

sev          = summary.get("severity_counts", {})
high_crit    = sev.get("high", 0) + sev.get("critical", 0)
last_ts      = str(summary.get("latest_alert_timestamp", "—"))[:19]

# ── KPI ROW ──
k1, k2, k3, k4 = st.columns(4)
k1.metric("📡  Total Events Ingested",   summary.get("alert_count", 0))
k2.metric("🔗  Open Investigations",      summary.get("open_incident_count", 0))
k3.metric("🔴  Critical / High Threats",  high_crit)
k4.metric("🕐  Latest Telemetry",         last_ts)

st.markdown("---")

# ─────────────────────────────────────────────────────
# MAIN TABS
# ─────────────────────────────────────────────────────
tabs = st.tabs([
    "📊  SOC Overview",
    "📡  Live Alerts",
    "🔗  Incidents",
    "🧠  AI Copilot",
    "🛡️  Playbooks",
    "⚙️  System Health",
])

# ══════════════════════════════════════════════════════
# TAB 1 — SOC OVERVIEW
# ══════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("""<div class='guide-box'>
    <b>What is this?</b>  A live security posture snapshot of your environment.
    The ring chart breaks down alert severity. If you see <b>Critical or High</b> alerts, immediately jump to
    the <b>Incidents</b> tab, correlate them, and trigger an <b>AI Copilot</b> investigation.
    </div>""", unsafe_allow_html=True)

    col_chart, col_status = st.columns([1, 1], gap="large")

    with col_chart:
        st.markdown("<div class='section-title'>Alert Severity Breakdown</div>", unsafe_allow_html=True)
        if sev:
            color_map = {"critical":"#EF4444","high":"#F97316","medium":"#EAB308","low":"#22C55E","unknown":"#6B7280"}
            labels  = list(sev.keys())
            values  = list(sev.values())
            colors  = [color_map.get(l,"#6B7280") for l in labels]
            fig = go.Figure(go.Pie(
                labels=labels, values=values, hole=0.65,
                marker=dict(colors=colors, line=dict(color="#0B0F19", width=2)),
                textinfo="percent+label",
                textfont=dict(size=13, color="#fff"),
            ))
            fig.update_layout(
                margin=dict(t=10,b=10,l=10,r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                showlegend=True,
                legend=dict(font=dict(color="#9CA3AF"), bgcolor="rgba(0,0,0,0)"),
                height=300,
            )
            st.plotly_chart(fig, use_container_width=False)
        else:
            st.info("No alert data available.")

    with col_status:
        st.markdown("<div class='section-title'>Integration Status</div>", unsafe_allow_html=True)
        st.success("✅  Wazuh SIEM Agent: Connected")
        st.success("✅  AI Engine (Groq LLM): Online")
        st.success("✅  Backend Database: Active")
        if high_crit > 0:
            st.error(f"⚠️  Action Required — {high_crit} High/Critical threat(s) need triage!")
        else:
            st.success("✅  No Critical Threats — Environment Stable")

# ══════════════════════════════════════════════════════
# TAB 2 — LIVE ALERTS
# ══════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("""<div class='guide-box'>
    <b>What is this?</b>  Raw security events forwarded by your Wazuh agents in real-time.
    Each row is a single event. Filter by severity to focus only on what matters.
    <b>Critical &amp; High</b> events should be correlated into Incidents immediately.
    </div>""", unsafe_allow_html=True)

    fc1, fc2 = st.columns([1,4])
    with fc1:
        sev_filter = st.selectbox("Severity Filter", ["All","critical","high","medium","low"])
    with fc2:
        if st.button("🔄 Refresh Alerts"):
            st.cache_data.clear()

    params = {"limit":100, "offset":0}
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
            st.info("No alerts found for selected filter.")
    except Exception as e:
        st.error(f"Could not load alerts — {e}")

# ══════════════════════════════════════════════════════
# TAB 3 — INCIDENTS
# ══════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("""<div class='guide-box'>
    <b>What is this?</b>  SentinelIQ automatically groups related alerts into <b>Incidents</b> based on
    timing, agent, and rule patterns. An incident is the unit you investigate — not individual alerts.
    Pick an Incident ID and take it to the <b>AI Copilot</b> tab for automated analysis.
    </div>""", unsafe_allow_html=True)

    if st.button("🔄 Refresh Incidents"):
        st.cache_data.clear()

    try:
        incidents = api_get("/api/incidents")
        if incidents:
            st.dataframe(pd.DataFrame(incidents), hide_index=True, height=300)
        else:
            st.info("No incidents correlated yet.")
    except Exception as e:
        st.error(str(e))

    st.markdown("---")
    st.markdown("<div class='section-title'>Incident Evidence Viewer</div>", unsafe_allow_html=True)
    inv_id = st.number_input("Incident ID to inspect", min_value=1, step=1, value=1, key="inv_id")
    if st.button("Load Incident Timeline"):
        try:
            detail = api_get(f"/api/incidents/{inv_id}")
            st.json(detail)
        except Exception as e:
            st.error(str(e))

# ══════════════════════════════════════════════════════
# TAB 4 — AI COPILOT
# ══════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("""<div class='guide-box'>
    <b>What is this?</b>  SentinelIQ AI Copilot is your automated Tier-2 analyst.
    Select an Incident, choose a task, and the AI will read all related alerts and produce a
    <b>plain-English report</b> with remediation steps.<br><br>
    ⚡ <b>Tip:</b> If you already ran an analysis and click again, the system will tell you it already exists.
    Use <b>"Force Re-run"</b> if you want a fresh analysis.
    </div>""", unsafe_allow_html=True)

    left, right = st.columns([1, 2], gap="large")

    TASK_DESCRIPTIONS = {
        "triage":        "🔍 Triage — Quick first-look: what happened and how urgent is it?",
        "investigation": "🧪 Investigation — Deep-dive: attack timeline, affected systems, evidence chain.",
        "response":      "🛡️ Response — Windows remediation commands to contain and fix the threat.",
        "manager":       "👔 Manager Brief — Simple English summary for non-technical managers.",
        "report":        "📄 Report — Full structured incident report (downloadable).",
    }

    with left:
        st.markdown("<div class='section-title'>AI Task Configuration</div>", unsafe_allow_html=True)
        ai_inc_id   = st.number_input("Target Incident ID", min_value=1, step=1, value=1, key="ai_id")
        task_choice = st.radio("Analysis Module", list(TASK_DESCRIPTIONS.keys()),
                               format_func=lambda x: TASK_DESCRIPTIONS[x])
        force_rerun = st.checkbox("Force Re-run (ignore cached result)")
        run_ai      = st.button("🚀  Run AI Analysis", type="primary", use_container_width=True)

    with right:
        if run_ai:
            with st.spinner("SentinelIQ AI is analyzing all correlated evidence…"):
                try:
                    res = api_post(
                        f"/api/incidents/{ai_inc_id}/analyze",
                        {"task": task_choice, "force": force_rerun}
                    )

                    if res.get("status") == "success":
                        ai = res.get("result", {})
                        model_info = f"Model: `{ai.get('model','?')}`  |  Task: `{task_choice.upper()}`"
                        st.success(f"✅  Analysis complete — {model_info}")

                        # ── TRIAGE ──────────────────────────────────────
                        if task_choice == "triage":
                            st.markdown("#### 🔍 What Happened (Plain English)")
                            st.info(ai.get("finding", "No finding provided."))
                            conf = ai.get("confidence_label","unknown").upper()
                            st.markdown(f"**Analyst Confidence:** `{conf}`")

                            actions = ai.get("recommended_actions", [])
                            if actions:
                                st.markdown("#### ✅ Recommended Next Steps")
                                for a in actions: st.markdown(f"- {a}")

                            unknowns = ai.get("unknowns", [])
                            if unknowns:
                                st.markdown("#### ❓ What We Don't Know Yet")
                                for u in unknowns: st.markdown(f"- {u}")

                        # ── INVESTIGATION ────────────────────────────────
                        elif task_choice == "investigation":
                            st.markdown("#### 🔍 Finding")
                            st.info(ai.get("finding","—"))

                            tl = ai.get("timeline_summary","")
                            if tl:
                                st.markdown("#### ⏱️ Attack Timeline")
                                st.write(tl)

                            steps = ai.get("next_investigation_steps",[]) + ai.get("recommended_actions",[])
                            if steps:
                                st.markdown("#### 🔬 Analyst Investigation Steps")
                                for s in steps: st.markdown(f"- {s}")

                            with st.expander("Evidence References"):
                                st.write(ai.get("evidence_refs",[]))

                        # ── RESPONSE (Windows-focused) ────────────────────
                        elif task_choice == "response":
                            st.markdown("#### 🛑 Threat Summary")
                            st.warning(ai.get("finding","—"))
                            st.markdown(f"**Reason for response:** {ai.get('reason','—')}")

                            impact = ai.get("impact","")
                            if impact:
                                st.error(f"⚠️ Potential Impact: {impact}")

                            actions = ai.get("recommended_actions", [])
                            if actions:
                                st.markdown("#### 🪟 Windows Remediation Steps")
                                st.caption("Copy-paste these commands into an elevated PowerShell window on the affected host:")
                                for step in actions:
                                    step_lower = step.lower()
                                    # Show as PowerShell code block
                                    if any(k in step_lower for k in
                                           ["powershell","netsh","firewall","block","stop-process",
                                            "taskkill","disable","remove","get-","set-","new-","invoke-","wmic"]):
                                        st.code(step, language="powershell")
                                    else:
                                        st.markdown(f"- {step}")

                            rollback = ai.get("rollback",[])
                            if rollback:
                                with st.expander("↩️ Rollback Plan (If action causes issues)"):
                                    for rb in rollback: st.markdown(f"- {rb}")

                            verify = ai.get("verification",[])
                            if verify:
                                with st.expander("✔️ Verification Steps"):
                                    for v in verify: st.markdown(f"- {v}")

                        # ── MANAGER ──────────────────────────────────────
                        elif task_choice == "manager":
                            st.markdown("#### 📋 Executive Summary (Non-Technical)")
                            col_m1, col_m2 = st.columns(2)
                            with col_m1:
                                st.markdown(f"**What happened:**\n\n{ai.get('what_happened','—')}")
                                st.markdown(f"**Why it matters:**\n\n{ai.get('why_it_might_matter','—')}")
                            with col_m2:
                                systems = ai.get("affected_systems",[])
                                if systems:
                                    st.markdown("**Affected Systems:**")
                                    for s in systems: st.markdown(f"- 💻 {s}")
                            known = ai.get("what_we_know",[])
                            if known:
                                st.markdown("**What we know:**")
                                for k in known: st.markdown(f"- {k}")
                            unknown = ai.get("what_we_do_not_know",[])
                            if unknown:
                                st.markdown("**What we still need to find out:**")
                                for u in unknown: st.markdown(f"- {u}")

                        # ── REPORT ───────────────────────────────────────
                        elif task_choice == "report":
                            st.markdown("#### 📄 Incident Report")
                            st.markdown(f"**Executive Summary:**\n\n{ai.get('executive_summary','—')}")
                            st.markdown(f"**Technical Summary:**\n\n{ai.get('technical_summary','—')}")
                            timeline = ai.get("timeline",[])
                            if timeline:
                                st.markdown("**Timeline:**")
                                for t in timeline: st.markdown(f"- {t}")
                            st.download_button(
                                "⬇️  Download Full Report (JSON)",
                                data=json.dumps(ai, indent=2, default=str),
                                file_name=f"SentinelIQ_Incident_{ai_inc_id}_Report.json",
                                mime="application/json",
                            )
                    else:
                        st.json(res)

                except RuntimeError as e:
                    err = str(e)
                    # ── ALREADY EXISTS — nice message, not a raw error ──
                    if "already exists" in err.lower() or "409" in err:
                        st.warning(
                            f"⚠️  A **{task_choice}** analysis for Incident #{ai_inc_id} already exists in the database.\n\n"
                            "To view it, check the Incident Evidence Viewer (Incidents tab). "
                            "If you want a **fresh analysis**, tick the **Force Re-run** checkbox above and click Run again."
                        )
                    else:
                        st.error(f"AI Analysis Failed — {err}")
                except Exception as e:
                    st.error(f"Unexpected error — {e}")

# ══════════════════════════════════════════════════════
# TAB 5 — WINDOWS REMEDIATION PLAYBOOKS
# ══════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("""<div class='guide-box'>
    <b>What is this?</b>  Step-by-step Windows remediation playbooks.
    Each playbook is a real-world Standard Operating Procedure (SOP).
    <b>Do NOT run these commands without confirming the target machine with your team lead.</b>
    All commands require an elevated (Administrator) PowerShell session on the affected host.
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Windows Incident Response Playbooks</div>", unsafe_allow_html=True)

    with st.expander("🚫  Playbook 1 — Block a Malicious IP Address (Windows Firewall)"):
        st.markdown("""
**When to use:** An attacker IP has been identified in the alert or AI analysis and needs to be blocked at the host level.

**Step 1 — Open elevated PowerShell** (Right-click → Run as Administrator)

**Step 2 — Block inbound traffic from attacker IP:**
""")
        st.code('New-NetFirewallRule -DisplayName "SentinelIQ-Block-Attacker" -Direction Inbound -RemoteAddress <ATTACKER_IP> -Action Block -Protocol Any', language="powershell")
        st.markdown("**Step 3 — Block outbound traffic (prevent callback/beaconing):**")
        st.code('New-NetFirewallRule -DisplayName "SentinelIQ-Block-Outbound" -Direction Outbound -RemoteAddress <ATTACKER_IP> -Action Block -Protocol Any', language="powershell")
        st.markdown("**Step 4 — Verify the rule was applied:**")
        st.code('Get-NetFirewallRule -DisplayName "SentinelIQ-Block-Attacker" | Format-List', language="powershell")
        st.markdown("**Rollback (if needed):**")
        st.code('Remove-NetFirewallRule -DisplayName "SentinelIQ-Block-Attacker"\nRemove-NetFirewallRule -DisplayName "SentinelIQ-Block-Outbound"', language="powershell")

    with st.expander("💀  Playbook 2 — Kill a Malicious Process (Taskkill / PowerShell)"):
        st.markdown("""
**When to use:** A suspicious process (e.g., reverse shell, ransomware, crypto-miner) is identified by name or PID in the AI analysis.

**Step 1 — List all processes and find suspect:**
""")
        st.code("Get-Process | Where-Object { $_.Name -like '*<PROCESS_NAME>*' } | Select-Object Id, Name, CPU, Path", language="powershell")
        st.markdown("**Step 2 — Kill by process name:**")
        st.code("Stop-Process -Name '<PROCESS_NAME>' -Force -Confirm:$false", language="powershell")
        st.markdown("**Step 3 — Kill by PID (if name is unknown):**")
        st.code("Stop-Process -Id <PID> -Force", language="powershell")
        st.markdown("**Step 4 — Verify it's gone:**")
        st.code("Get-Process -Name '<PROCESS_NAME>' -ErrorAction SilentlyContinue", language="powershell")

    with st.expander("🔒  Playbook 3 — Isolate a Compromised Machine from Network"):
        st.markdown("""
**When to use:** A host is confirmed compromised and needs to be isolated to prevent lateral movement.

**Step 1 — Block all inbound and outbound via Windows Firewall:**
""")
        st.code("""Set-NetFirewallProfile -All -DefaultInboundAction Block
Set-NetFirewallProfile -All -DefaultOutboundAction Block""", language="powershell")
        st.markdown("**Step 2 — Keep only RDP open so YOU can still reach it (replace YOUR_IP):**")
        st.code('New-NetFirewallRule -DisplayName "SOC-Admin-Access" -Direction Inbound -RemoteAddress <YOUR_SOC_IP> -LocalPort 3389 -Protocol TCP -Action Allow', language="powershell")
        st.markdown("**Rollback — Restore normal firewall defaults:**")
        st.code("""Set-NetFirewallProfile -All -DefaultInboundAction Allow
Set-NetFirewallProfile -All -DefaultOutboundAction Allow
Remove-NetFirewallRule -DisplayName "SOC-Admin-Access" """, language="powershell")

    with st.expander("🔑  Playbook 4 — Disable a Compromised User Account"):
        st.markdown("""
**When to use:** A user account shows signs of compromise (lateral movement, brute force success, impossible travel).

**Step 1 — Disable the account in Active Directory (run on Domain Controller):**
""")
        st.code("Disable-ADAccount -Identity '<USERNAME>'", language="powershell")
        st.markdown("**Step 2 — Force sign out all active sessions:**")
        st.code("Get-CimInstance -ClassName Win32_Process | Where-Object { $_.GetOwner().User -eq '<USERNAME>' } | Invoke-CimMethod -MethodName Terminate", language="powershell")
        st.markdown("**Step 3 — Reset the password (mandatory before re-enable):**")
        st.code("Set-ADAccountPassword -Identity '<USERNAME>' -Reset -NewPassword (ConvertTo-SecureString '<STRONG_NEW_PASSWORD>' -AsPlainText -Force)", language="powershell")
        st.markdown("**Step 4 — Re-enable when cleared:**")
        st.code("Enable-ADAccount -Identity '<USERNAME>'", language="powershell")

    with st.expander("🔐  Playbook 5 — Block a Malicious Port or Service"):
        st.markdown("""
**When to use:** A specific port is being exploited (e.g., SMB 445, RDP 3389 from unknown IPs).

**Step 1 — Find what is listening on a port:**
""")
        st.code("netstat -ano | findstr ':<PORT>'", language="powershell")
        st.markdown("**Step 2 — Block the port inbound in Windows Firewall:**")
        st.code('New-NetFirewallRule -DisplayName "SentinelIQ-Block-Port" -Direction Inbound -LocalPort <PORT> -Protocol TCP -Action Block', language="powershell")
        st.markdown("**Step 3 — Stop and disable the service using the port:**")
        st.code("Stop-Service -Name '<SERVICE_NAME>' -Force\nSet-Service -Name '<SERVICE_NAME>' -StartupType Disabled", language="powershell")

    with st.expander("📋  Playbook 6 — Collect Forensic Evidence (Before Cleanup)"):
        st.markdown("""
**When to use:** Before removing malware or isolating, collect evidence for forensic analysis.

**Step 1 — Export all running processes with full paths:**
""")
        st.code("Get-Process | Select-Object Id, Name, Path, CPU, StartTime | Export-Csv C:\\SOC_Evidence\\processes_$(Get-Date -f yyyyMMdd_HHmm).csv -NoTypeInformation", language="powershell")
        st.markdown("**Step 2 — Export all active network connections:**")
        st.code("netstat -anob > C:\\SOC_Evidence\\netstat_$(Get-Date -f yyyyMMdd_HHmm).txt", language="powershell")
        st.markdown("**Step 3 — Export event logs (Security channel):**")
        st.code("wevtutil epl Security C:\\SOC_Evidence\\Security_$(Get-Date -f yyyyMMdd_HHmm).evtx", language="powershell")
        st.markdown("**Step 4 — Create evidence directory first:**")
        st.code("New-Item -ItemType Directory -Path C:\\SOC_Evidence -Force", language="powershell")

# ══════════════════════════════════════════════════════
# TAB 6 — SYSTEM HEALTH
# ══════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("""<div class='guide-box'>
    <b>What is this?</b>  Check connectivity between SentinelIQ components.
    If alerts are not appearing, use this tab to verify that Wazuh and the backend API are reachable.
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Component Health Check</div>", unsafe_allow_html=True)

    if st.button("🔄  Run Health Check Now"):
        with st.spinner("Checking connectivity…"):
            try:
                health = api_get("/api/source/status")
                st.success("✅  Backend API: Reachable")
                st.json(health)
            except Exception as e:
                st.error(f"❌  Backend API Unreachable — {e}")

    st.markdown("---")
    st.markdown("<div class='section-title'>Manual Testing Guide</div>", unsafe_allow_html=True)
    st.markdown("""
To verify your Wazuh agent is sending real alerts to SentinelIQ:

**Windows agent — Trigger a test event (PowerShell):**
""")
    st.code("""# Simulate a failed login event (write to Windows Application log)
Write-EventLog -LogName Application -Source "Application" -EventId 1001 -Message "SentinelIQ test event - simulated alert"

# Or trigger a real detection: create a file in a monitored path
echo "SentinelIQ test" > C:\\Users\\Public\\sentineliq_test.txt""", language="powershell")
    st.markdown("**Check if the event arrived in the database:**")
    st.code("""# Run on Debian backend
curl -H "Authorization: Bearer <TOKEN>" https://<CLOUDFLARE_URL>/api/dashboard/summary""", language="bash")
