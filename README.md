# 🎼 SynergyMesh — AI Agent Society

An AI agent society consisting of **5 major bodies** working together in perfect harmony and synergy:

| Body | Role |
|------|------|
| 🔵 **Orchestrator** | Coordinates the swarm, dispatches tasks, manages workflow |
| 🩵 **Researcher** | Gathers information, scans best practices & documentation |
| 🟢 **Developer** | Writes code, drafts solutions, implements features |
| 🟡 **Critic** | Reviews quality, approves or sends work back for revision |
| 🟣 **Executor (You)** | Synthesizes deliverables and ships the final output |

The collaboration pipeline: **Dispatch → Discovery → Build → Review → Ship**, with live feedback loops (the Critic can bounce work back to the Developer) and a global **Synergy Score** that rises as agents cooperate.

---

## 📁 What's in this repo

| File | Description |
|------|-------------|
| `streamlit_app.py` | ⭐ **Streamlit web dashboard** (recommended) — live message feed, agent roster, harmony meter |
| `requirements.txt` | Python dependencies (`streamlit>=1.30`) |
| `live_agent_society.py` | Terminal version with real-time typing animation & color-coded agents |
| `ai_agent_society.py` | Core engine — shared state, message protocol, 5-phase workflow |
| `web_agent_society.py` | Dependency-free Python HTTP server + dashboard (port 8000) |
| `index.html` | Static single-file dashboard (browser-only agent engine) |
| `vercel_app/` | Drop-in folder for deploying the static dashboard to Vercel |

---

## 🚀 Run it locally

### Option A — Streamlit dashboard (recommended)
```bash
pip install streamlit
streamlit run streamlit_app.py
# opens http://localhost:8501
```

> **Windows tip:** if `streamlit` isn't recognized, use:
> ```powershell
> py -m pip install streamlit
> py -m streamlit run streamlit_app.py
> ```

### Option B — Terminal society
```bash
python live_agent_society.py
```

### Option C — Zero-dependency web server
```bash
python web_agent_society.py
# open http://localhost:8000
```

---

## ☁️ Deploy to Streamlit Cloud (permanent URL)

1. Push this repo to GitHub.
2. Go to **https://share.streamlit.io** → sign in with GitHub → *New app*.
3. Set **Main file path** to `streamlit_app.py` → **Deploy**.
4. You get a permanent `https://<your-app>.streamlit.app` link that works from any device.

### Deploy the static version to Vercel
Upload only the contents of `vercel_app/` (`index.html` + `vercel.json`) with **no build command**.

---

## 🔄 How the agents achieve synergy

1. **Orchestrator** receives your task and decomposes it into phases.
2. **Researcher** feeds context & best practices into shared memory.
3. **Developer** builds the solution using that research.
4. **Critic** reviews; on rejection the task loops back to the Developer.
5. **Executor** delivers the final artifact and reports results.

Every hand-off is logged in the live feed, and the Harmony Meter tracks how well the five bodies collaborate. ✨
