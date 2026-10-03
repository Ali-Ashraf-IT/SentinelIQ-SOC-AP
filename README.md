# 🛡️ SentinelIQ Enterprise SIEM

> **AI-Augmented Security Information & Event Management Platform**  
> Real-time Wazuh integration · Groq LLM-powered threat analysis · Automated incident response

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=flat-square&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Cloud-FF4B4B?style=flat-square&logo=streamlit)
![Wazuh](https://img.shields.io/badge/Wazuh-v4.14-00B4D8?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-LLM-F55036?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📌 Overview

**SentinelIQ** is a production-grade SOC (Security Operations Center) platform that connects to a live **Wazuh SIEM** deployment, ingests real-time security alerts, correlates them into incidents, and uses **Groq AI (LLaMA 3.3 70B)** to automatically triage, investigate, and recommend remediation steps — all displayed in a professional enterprise dashboard.

### 🎯 Key Features

- 📡 **Real-time Alert Ingestion** from Wazuh via REST API + Wazuh Indexer
- 🔗 **Automatic Incident Correlation** — groups related alerts into investigations
- 🧠 **AI Copilot (Groq LLaMA 3.3 70B)** — 5 AI analysis modes
- 🛡️ **Windows Remediation Playbooks** — copy-paste ready PowerShell SOPs
- 📊 **Enterprise Dark Dashboard** — IBM QRadar / Microsoft Sentinel inspired UI
- 🔄 **Auto-Ingest Cron** — Pulls new alerts every 2 minutes automatically
- 🔐 **Bearer Token Auth + Rate Limiting** on all API endpoints
- ☁️ **Cloudflare Tunnel** — Secure public access to local Debian backend

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SENTINELIQ ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Windows Endpoint                                                │
│  ┌─────────────┐     TCP/1514      ┌──────────────────────────┐ │
│  │ Wazuh Agent │ ─────────────────▶│   Wazuh Manager v4.14   │ │
│  │  (ossec)    │                   │   + Wazuh Indexer        │ │
│  └─────────────┘                   │   (Debian Local)         │ │
│                                    └──────────┬───────────────┘ │
│                                               │ REST API         │
│                                    ┌──────────▼───────────────┐ │
│                                    │   SentinelIQ Backend     │ │
│                                    │   FastAPI + SQLite       │ │
│                                    │   • Normalize            │ │
│                                    │   • Deduplicate          │ │
│                                    │   • Correlate            │ │
│                                    │   • AI Analysis (Groq)   │ │
│                                    └──────────┬───────────────┘ │
│                                               │ Cloudflare Tunnel│
│                                    ┌──────────▼───────────────┐ │
│                                    │   Streamlit Cloud        │ │
│                                    │   SentinelIQ Dashboard   │ │
│                                    └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
SentinelIQ-SOC-AP/
│
├── app.py                          # Streamlit Frontend (deploy on Streamlit Cloud)
├── requirements.txt                # Python dependencies
├── .env                            # Backend environment variables (Debian only)
├── README.md                       # This file
│
├── backend/
│   ├── main.py                     # FastAPI app entry point + rate limiter
│   ├── config.py                   # Settings via pydantic-settings + .env
│   ├── ingest.py                   # Core ingestion logic (fetch → normalize → store)
│   │
│   ├── api/
│   │   ├── alerts.py               # GET /api/alerts
│   │   ├── incidents.py            # GET/POST /api/incidents + AI analyze
│   │   ├── health.py               # GET /api/source/status
│   │   └── investigations.py       # GET /api/dashboard/summary
│   │
│   ├── db/
│   │   ├── models.py               # SQLAlchemy ORM models (Alert, Incident)
│   │   ├── repository.py           # DB query functions
│   │   └── session.py              # DB session factory
│   │
│   ├── llm/
│   │   ├── router.py               # LLM task router (Groq / Bedrock)
│   │   ├── triage.py               # Triage analysis prompt
│   │   ├── investigation.py        # Investigation analysis prompt
│   │   ├── response.py             # Response planning prompt
│   │   ├── manager_explanation.py  # Manager brief prompt
│   │   ├── report.py               # Full report prompt
│   │   └── providers/
│   │       ├── groq_provider.py    # Groq API integration
│   │       └── bedrock_provider.py # AWS Bedrock integration
│   │
│   ├── processing/
│   │   ├── normalize.py            # Wazuh hit → NormalizedAlert
│   │   ├── deduplicate.py          # Fingerprint-based dedup
│   │   ├── correlate.py            # Alert → Incident grouping
│   │   ├── fingerprint.py          # SHA256 fingerprint builder
│   │   ├── cursor.py               # Ingestion cursor management
│   │   └── risk_rules.py           # Severity scoring rules
│   │
│   ├── schemas/
│   │   ├── alert.py                # NormalizedAlert Pydantic model
│   │   ├── analysis.py             # AI result schemas (Triage, Investigation...)
│   │   └── runtime.py              # IngestionResponse schema
│   │
│   └── wazuh/
│       ├── base.py                 # Abstract WazuhSourceClient
│       ├── local_client.py         # Local Wazuh API client
│       ├── aws_client.py           # AWS Wazuh API client
│       └── factory.py              # Client factory (local vs aws)
```

---

## ⚙️ Requirements

### Backend (Debian Linux)
- Python 3.13+
- Wazuh Manager v4.x (local or AWS)
- Wazuh Indexer (OpenSearch)
- Cloudflare Tunnel (`cloudflared`)
- SQLite (default) or PostgreSQL

### Frontend (Streamlit Cloud)
- Streamlit Community Cloud account
- GitHub repository with `app.py`

### AI (Groq)
- Free Groq API key from [console.groq.com](https://console.groq.com)
- Model: `llama-3.3-70b-versatile`

---

## 🚀 Installation & Setup

### Step 1 — Clone & Virtual Environment (Debian)

```bash
git clone https://github.com/<YOUR_USERNAME>/SentinelIQ-SOC-AP.git /opt/soc-app
cd /opt/soc-app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 2 — Configure `.env`

```bash
nano /opt/soc-app/.env
```

```env
# App
APP_NAME=SentinelIQ Enterprise SIEM
APP_VERSION=2.0.0

# API Security
SOC_API_TOKEN=YourSecretTokenHere

# Database
DATABASE_URL=sqlite:///./soc_app.db

# Wazuh Source (local or aws)
WAZUH_SOURCE=local
LOCAL_WAZUH_API_URL=https://127.0.0.1:55000
LOCAL_WAZUH_INDEXER_URL=https://127.0.0.1:9200
WAZUH_API_USERNAME=admin
WAZUH_API_PASSWORD=YourWazuhPassword
WAZUH_INDEXER_USERNAME=admin
WAZUH_INDEXER_PASSWORD=YourIndexerPassword
WAZUH_VERIFY_TLS=false

# Ingestion
FETCH_LIMIT=500
LOOKBACK_MINUTES=30
INITIAL_SYNC_MODE=lookback
CORRELATION_WINDOW_MINUTES=10
CURSOR_OVERLAP_SECONDS=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Groq AI
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_USE_JSON_MODE=true
GROQ_TIMEOUT_SECONDS=30

# LLM Task Routing
LLM_TRIAGE_PROVIDER=groq
LLM_TRIAGE_MODEL_ID=llama-3.3-70b-versatile
LLM_INVESTIGATION_PROVIDER=groq
LLM_INVESTIGATION_MODEL_ID=llama-3.3-70b-versatile
LLM_RESPONSE_PROVIDER=groq
LLM_RESPONSE_MODEL_ID=llama-3.3-70b-versatile
LLM_MANAGER_PROVIDER=groq
LLM_MANAGER_MODEL_ID=llama-3.3-70b-versatile
LLM_REPORT_PROVIDER=groq
LLM_REPORT_MODEL_ID=llama-3.3-70b-versatile
```

### Step 3 — SystemD Service

```bash
sudo nano /etc/systemd/system/soc-backend.service
```

```ini
[Unit]
Description=SOC App FastAPI Backend
After=network.target

[Service]
User=root
WorkingDirectory=/opt/soc-app
ExecStart=/opt/soc-app/.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable soc-backend
sudo systemctl start soc-backend
sudo systemctl status soc-backend
```

### Step 4 — Auto Ingestion Cron (Every 2 min)

```bash
cat > /tmp/soc_cron.txt << 'CRONEOF'
*/2 * * * * /usr/bin/curl -s -X POST -H 'Authorization: Bearer YourSecretTokenHere' http://localhost:8000/api/ingestion/run >> /var/log/soc-ingest.log 2>&1
CRONEOF

crontab /tmp/soc_cron.txt
crontab -l
```

### Step 5 — Cloudflare Tunnel

```bash
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
cloudflared tunnel --url http://localhost:8000
```

### Step 6 — Streamlit Cloud Deploy

1. Push `app.py` + `requirements.txt` to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → connect repo → select `app.py`
3. Add Secrets:

```toml
BACKEND_API_URL = "https://your-tunnel.trycloudflare.com"
BACKEND_API_TOKEN = "YourSecretTokenHere"
```

---

## 🖥️ Dashboard Tabs

| Tab | Description |
|-----|-------------|
| 📊 SOC Overview | Severity ring chart, integration status, threat level |
| 📡 Live Alerts | All ingested events, filterable by severity |
| 🔗 Incidents | Auto-correlated incident groups + evidence viewer |
| 🧠 AI Copilot | 5 AI analysis modes — human-readable output |
| 🛡️ Playbooks | 6 Windows PowerShell SOPs for real remediation |
| ⚙️ System Health | Connectivity check + manual test guide |

---

## 🧠 AI Copilot Modes

| Mode | What it does |
|------|-------------|
| **Triage** | Quick first-look: what happened, confidence level, immediate steps |
| **Investigation** | Deep-dive: full attack timeline, evidence chain, next steps |
| **Response** | Windows PowerShell remediation commands (copy-paste ready) |
| **Manager Brief** | Plain-English executive summary for non-technical management |
| **Report** | Full structured incident report — downloadable JSON |

---

## 🔌 API Reference

All endpoints require: `Authorization: Bearer <SOC_API_TOKEN>`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check (no auth required) |
| `GET` | `/api/source/status` | Wazuh + Indexer connectivity |
| `GET` | `/api/alerts` | List alerts (`?severity=high&limit=100`) |
| `GET` | `/api/alerts/{id}` | Single alert raw detail |
| `GET` | `/api/incidents` | List correlated incidents |
| `GET` | `/api/incidents/{id}` | Incident + all linked alerts |
| `POST` | `/api/incidents/{id}/analyze` | Run AI analysis |
| `GET` | `/api/dashboard/summary` | KPI counts for dashboard |
| `POST` | `/api/ingestion/run` | Manually trigger alert ingestion |

**AI Analyze Body:**
```json
{ "task": "triage", "force": true }
```
`task` options: `triage` | `investigation` | `response` | `manager` | `report`

---

## 🧪 Testing — Generate Real Wazuh Alerts

Run on the **Windows machine with Wazuh agent**:

```powershell
# Test 1 — FIM (File Integrity Monitoring)
"SentinelIQ Test" | Out-File C:\Users\ashraf\Desktop\fim_test.txt
Start-Sleep -Seconds 3
Remove-Item C:\Users\ashraf\Desktop\fim_test.txt

# Test 2 — Failed Logins (Brute Force simulation)
1..5 | ForEach-Object {
    net use \\localhost\IPC$ /user:FakeAttacker WrongPass 2>$null
    Start-Sleep -Seconds 1
}

# Test 3 — New Port Listening (Network change)
$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, 9999)
$listener.Start(); Start-Sleep -Seconds 10; $listener.Stop()
```

**Then trigger ingestion on Debian:**
```bash
curl -s -X POST \
  -H "Authorization: Bearer YourSecretTokenHere" \
  http://localhost:8000/api/ingestion/run | python3 -m json.tool
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `502 Bad Gateway` | `sudo systemctl restart soc-backend` |
| `IndentationError` on startup | Re-paste backend Python files using `cat << 'EOF' >` |
| AI returns `ValidationError` | Ensure `provider`, `model`, `prompt_version` have `= ""` default in `analysis.py` |
| Alerts not updating | Check crontab: `crontab -l` — if missing, re-run Step 4 |
| `Expecting value` curl error | Backend still starting — wait 5 seconds and retry |
| `!: event not found` in bash | Use file-based crontab method (Step 4) — avoids `!` expansion |
| Streamlit warnings sidebar | Remove `use_container_width=True` from all `st.dataframe()` calls |

---

## 🔐 Security Notes

> ⚠️ SentinelIQ is a **read-only monitoring and advisory platform**.  
> It never automatically executes actions on endpoints.

- All AI analysis output is **advisory only** — human analyst must review before acting
- Playbook commands require **manual execution** on affected hosts
- `.env` contains secrets — **add to `.gitignore` immediately**
- `SOC_API_TOKEN` should be a strong random string (32+ chars)
- Cloudflare Tunnel provides TLS — never expose port 8000 directly

---

## 📦 requirements.txt

```
fastapi
uvicorn[standard]
sqlalchemy
pydantic
pydantic-settings
python-dotenv
groq
boto3
requests
streamlit
pandas
plotly
```

---

## 📄 License

MIT License — Free to use, modify, and distribute with attribution.

---

## 👤 Author

**Ali Ashraf**  
SOC Engineer | Security Analyst  
Built with Wazuh, FastAPI, Groq AI, Streamlit, and Cloudflare

---

⭐ **Star this repo if SentinelIQ helped you build a better SOC!**
