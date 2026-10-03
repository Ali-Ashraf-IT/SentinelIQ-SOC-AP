import json
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Streamlit Page Config
st.set_page_config(page_title="AI SOC Analyst Dashboard", page_icon="🛡️", layout="wide")

# Secrets Streamlit Cloud Settings se load hotey hain
BACKEND_URL = st.secrets.get("BACKEND_API_URL", "").rstrip("/")
BACKEND_TOKEN = st.secrets.get("BACKEND_API_TOKEN", "")

if not BACKEND_URL or not BACKEND_TOKEN:
    st.error("Backend configuration missing! Add BACKEND_API_URL and BACKEND_API_TOKEN in Streamlit Secrets.")
    st.stop()

HEADERS = {"Authorization": f"Bearer {BACKEND_TOKEN}"}

# Helper API functions
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

# Header Title
st.title("🛡️ AI-Powered SOC Analyst Operations")
st.caption("Evidence-first Wazuh SIEM Monitoring. AI Analysis is on-demand and read-only.")

# Top Metrics Row
try:
    summary = api_get("/api/dashboard/summary")
except Exception as exc:
    st.error(f"Backend Server Unavailable: {exc}")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Alerts", summary.get("alert_count", 0))
c2.metric("Open Incidents", summary.get("open_incident_count", 0))
sev = summary.get("severity_counts", {})
c3.metric("High / Critical", sev.get("high", 0) + sev.get("critical", 0))
c4.metric("Latest Alert Time", str(summary.get("latest_alert_timestamp", "-")))

# Navigation Tabs
tabs = st.tabs([
    "SOC Overview",
    "Alerts Engine",
    "Correlated Incidents",
    "Incident Investigation",
    "AI SOC Analyst",
    "Response Plan",
    "Executive Reports",
    "System Health"
])

# Tab 1: Overview Chart
with tabs[0]:
    st.subheader("Severity Breakdown")
    chart_df = pd.DataFrame({"Severity": list(sev.keys()), "Count": list(sev.values())})
    if not chart_df.empty:
        st.plotly_chart(px.bar(chart_df, x="Severity", y="Count", text_auto=True, color="Severity"), )
    else:
        st.info("No alerts processed yet.")

# Tab 2: Alerts Table
with tabs[1]:
    st.subheader("Real-Time Ingested Alerts")
    severity_filter = st.selectbox("Filter Severity", ["All", "low", "medium", "high", "critical", "unknown"])
    params = {"limit": 100, "offset": 0}
    if severity_filter != "All":
        params["severity"] = severity_filter
    
    try:
        data = api_get("/api/alerts", params=params)
        items = data.get("items", [])
        if items:
            df = pd.DataFrame(items)
            st.dataframe(
                df[["id", "timestamp", "severity", "agent_name", "rule_id", "rule_description", "src_ip"]],
                
                hide_index=True
            )
            selected = st.number_input("Select Alert ID for JSON Detail", min_value=1, step=1, value=int(items[0]["id"]))
            if st.button("Load Raw Alert JSON"):
                st.json(api_get(f"/api/alerts/{selected}"))
        else:
            st.info("No alerts match the selected criteria.")
    except Exception as exc:
        st.error(str(exc))

# Tab 3: Correlated Incidents
with tabs[2]:
    st.subheader("Grouped Incidents")
    try:
        incidents = api_get("/api/incidents")
        if incidents:
            st.dataframe(pd.DataFrame(incidents), hide_index=True)
        else:
            st.info("No incidents correlated yet.")
    except Exception as exc:
        st.error(str(exc))

# Tab 4: Investigation Timeline
with tabs[3]:
    st.subheader("Incident Evidence & Timeline")
    inc_id = st.number_input("Incident ID", min_value=1, step=1, value=1, key="inv_id")
    if st.button("Fetch Incident Evidence"):
        try:
            detail = api_get(f"/api/incidents/{inc_id}")
            st.json(detail)
        except Exception as exc:
            st.error(str(exc))

# Tab 5: AI Analyst Trigger
with tabs[4]:
    st.subheader("Groq AI SOC Triage & Analysis")
    inc_id_ai = st.number_input("Incident ID", min_value=1, step=1, value=1, key="ai_inc_id")
    task_type = st.selectbox("AI Task", ["triage", "investigation", "manager"])
    if st.button("Run AI Analysis"):
        try:
            with st.spinner("Analyzing incident with Groq LLM..."):
                result = api_post(f"/api/incidents/{inc_id_ai}/analyze", {"task": task_type})
                st.json(result)
        except Exception as exc:
            st.error(str(exc))

# Tab 6: Response Recommendations
with tabs[5]:
    st.subheader("AI Response Recommendations")
    inc_resp_id = st.number_input("Incident ID", min_value=1, step=1, value=1, key="resp_id")
    if st.button("Generate Response Guidance"):
        try:
            res = api_post(f"/api/incidents/{inc_resp_id}/analyze", {"task": "response"})
            st.json(res)
        except Exception as exc:
            st.error(str(exc))
    st.warning("⚠️ All recommendations are advisory only. No actions are automatically executed on endpoints.")

# Tab 7: Reports
with tabs[6]:
    st.subheader("Generate Executive Incident Report")
    inc_rep_id = st.number_input("Incident ID", min_value=1, step=1, value=1, key="rep_id")
    if st.button("Generate Report"):
        try:
            rep = api_post(f"/api/incidents/{inc_rep_id}/analyze", {"task": "report"})
            st.json(rep)
            st.download_button(
                "Download Report JSON",
                data=json.dumps(rep, indent=2, default=str),
                file_name=f"incident-{inc_rep_id}-report.json",
                mime="application/json"
            )
        except Exception as exc:
            st.error(str(exc))

# Tab 8: System Health
with tabs[7]:
    st.subheader("Backend & Wazuh Connectivity Check")
    if st.button("Check Source Health"):
        try:
            health_status = api_get("/api/source/status")
            st.json(health_status)
        except Exception as exc:
            st.error(str(exc))
