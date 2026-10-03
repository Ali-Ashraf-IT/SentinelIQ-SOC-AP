import json
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="SentinelIQ-SOC-AP", page_icon="🛡️", layout="wide")

BACKEND_URL = st.secrets.get("BACKEND_API_URL", "").rstrip("/")
BACKEND_TOKEN = st.secrets.get("BACKEND_API_TOKEN", "")

if not BACKEND_URL or not BACKEND_TOKEN:
    st.error("Backend configuration is missing. Add BACKEND_API_URL and BACKEND_API_TOKEN to Streamlit secrets.")
    st.stop()

HEADERS = {"Authorization": f"Bearer {BACKEND_TOKEN}"}

def api_get(path: str, params: dict | None = None):
    r = requests.get(f"{BACKEND_URL}{path}", headers=HEADERS, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def api_post(path: str, body: dict | None = None):
    r = requests.post(f"{BACKEND_URL}{path}", headers=HEADERS, json=body or {}, timeout=60)
    if r.status_code >= 400:
        try:
            detail = r.json().get("detail", r.text)
        except Exception:
            detail = r.text
        raise RuntimeError(detail)
    return r.json()

st.title("AI SOC Analyst")
st.caption("Evidence-first Wazuh monitoring. AI is optional and never executes response actions.")

try:
    summary = api_get("/api/dashboard/summary")
except Exception as exc:
    st.error(f"Backend unavailable: {exc}")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Alerts", summary.get("alert_count", 0))
c2.metric("Open incidents", summary.get("open_incident_count", 0))
sev = summary.get("severity_counts", {})
c3.metric("High/Critical", sev.get("high", 0) + sev.get("critical", 0))
c4.metric("Last alert", summary.get("latest_alert_timestamp", "-"))

tabs = st.tabs([
    "SOC Overview",
    "Alerts",
    "Incidents",
    "Investigation",
    "AI Analyst",
    "Response Plan",
    "Reports",
    "System Health",
])

with tabs[0]:
    st.subheader("SOC Overview")
    chart_df = pd.DataFrame({"severity": list(sev.keys()), "count": list(sev.values())})
    if not chart_df.empty:
        st.plotly_chart(px.bar(chart_df, x="severity", y="count", text_auto=True), use_container_width=True)
    else:
        st.info("No alerts stored yet.")

with tabs[1]:
    st.subheader("Alerts")
    severity_filter = st.selectbox("Severity", ["All", "low", "medium", "high", "critical", "unknown"])
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
                use_container_width=True,
                hide_index=True,
            )
            selected = st.number_input("Alert ID", min_value=1, step=1, value=int(items[0]["id"]))
            if st.button("Load alert detail"):
                st.json(api_get(f"/api/alerts/{selected}"))
        else:
            st.info("No alerts match the filter.")
    except Exception as exc:
        st.error(str(exc))

with tabs[2]:
    st.subheader("Incidents")
    try:
        incident_items = api_get("/api/incidents")
        if incident_items:
            st.dataframe(pd.DataFrame(incident_items), use_container_width=True, hide_index=True)
        else:
            st.info("No incidents yet.")
    except Exception as exc:
        st.error(str(exc))

with tabs[3]:
    st.subheader("Investigation")
    incident_id = st.number_input("Incident ID", min_value=1, step=1, value=1, key="investigation_id")
    if st.button("Open incident timeline"):
        try:
            incident = api_get(f"/api/incidents/{incident_id}")
            st.json(incident)
        except Exception as exc:
            st.error(str(exc))

with tabs[4]:
    st.subheader("AI Analyst")
    incident_id = st.number_input("Incident ID", min_value=1, step=1, value=1, key="ai_id")
    task = st.selectbox("Analysis task", ["triage", "investigation", "manager"])
    if st.button("Request AI analysis"):
        try:
            result = api_post(f"/api/incidents/{incident_id}/analyze", {"task": task})
            st.json(result)
        except Exception as exc:
            st.error(str(exc))

with tabs[5]:
    st.subheader("Response Plan")
    incident_id = st.number_input("Incident ID", min_value=1, step=1, value=1, key="response_id")
    if st.button("Generate response recommendation"):
        try:
            result = api_post(f"/api/incidents/{incident_id}/analyze", {"task": "response"})
            st.json(result)
        except Exception as exc:
            st.error(str(exc))
    st.warning("Recommendations are informational. No containment or destructive action is executed by this app.")

with tabs[6]:
    st.subheader("Reports")
    incident_id = st.number_input("Incident ID", min_value=1, step=1, value=1, key="report_id")
    if st.button("Generate report"):
        try:
            result = api_post(f"/api/incidents/{incident_id}/analyze", {"task": "report"})
            st.json(result)
            st.download_button(
                "Download saved report JSON",
                data=json.dumps(result, indent=2, default=str),
                file_name=f"incident-{incident_id}-report.json",
                mime="application/json",
            )
        except Exception as exc:
            st.error(str(exc))

with tabs[7]:
    st.subheader("System Health")
    if st.button("Check Wazuh source"):
        try:
            status = api_get("/api/source/status")
            st.json(status)
        except Exception as exc:
            st.error(str(exc))
