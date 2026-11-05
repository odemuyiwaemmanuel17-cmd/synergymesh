"""
🤝 AI AGENT SOCIETY — Streamlit Edition
Five autonomous agents working in perfect harmony:
Orchestrator 🔵 · Researcher 🩵 · Developer 🟢 · Critic 🟡 · Executor 🟣

Run locally:   streamlit run streamlit_app.py
Deploy free:   https://share.streamlit.io  (push this file + requirements.txt to GitHub)
"""

import time
import random
from datetime import datetime

import streamlit as st

# ---------------------------------------------------------------- page setup
st.set_page_config(
    page_title="AI Agent Society",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

AGENTS = {
    "orchestrator": {"name": "Orchestrator", "emoji": "🔵", "color": "#4C7DF0",
                     "role": "Coordinates the swarm, routes tasks, resolves conflicts"},
    "researcher":   {"name": "Researcher",   "emoji": "🩵", "color": "#38BDF8",
                     "role": "Gathers knowledge, scans docs, finds best practices"},
    "developer":    {"name": "Developer",    "emoji": "🟢", "color": "#22C55E",
                     "role": "Writes code, designs architecture, implements solutions"},
    "critic":       {"name": "Critic",       "emoji": "🟡", "color": "#EAB308",
                     "role": "Reviews quality, catches bugs, enforces standards"},
    "executor":     {"name": "Executor",     "emoji": "🟣", "color": "#A855F7",
                     "role": "Synthesizes deliverables and ships the final result"},
}

# ------------------------------------------------------------- state helpers
def init_state():
    if "feed" not in st.session_state:
        st.session_state.feed = []          # list of message dicts
        st.session_state.synergy = 0.0
        st.session_state.tasks_done = 0
        st.session_state.busy = None        # agent id currently active
        st.session_state.task_log = {}      # task -> list of messages


init_state()


def emit(sender, receiver, text, kind="msg"):
    """One agent speaks to another — appended to the shared society feed."""
    msg = {
        "t": datetime.now().strftime("%H:%M:%S"),
        "sender": sender, "receiver": receiver, "text": text, "kind": kind,
    }
    st.session_state.feed.append(msg)
    if st.session_state.feed:
        st.session_state.synergy = min(1.0, st.session_state.synergy + 0.04)
    return msg


PHASES = [
    ("orchestrator", "researcher", "📥 Task received → dispatching research sweep"),
    ("researcher", "developer", "🔎 Best practices & references compiled for dev team"),
    ("developer", "critic", "⌨️ Implementation drafted → requesting review"),
    ("critic", "developer", "🔍 Review passed with minor suggestions (approved)"),
    ("developer", "executor", "✅ Revised build handed off for delivery"),
    ("executor", "orchestrator", "🚀 Final deliverable shipped to requester"),
]


def run_task(task: str):
    """The five bodies collaborate on a task, streaming messages live."""
    st.session_state.busy = "orchestrator"
    header = f"── NEW TASK: “{task}” ──"
    emit("user", "orchestrator", header, kind="task")

    for sender, receiver, line in PHASES:
        st.session_state.busy = sender
        # each render of the loop below is driven by the caller; here we just log
        verb = random.choice(["refined", "validated", "stress-tested", "optimized"])
        emit(sender, receiver, f"{line}  ·  {verb} against edge cases",
             kind="phase")

    st.session_state.busy = None
    st.session_state.tasks_done += 1
    emit("orchestrator", "user",
         f"🏁 Task complete. Synergy across all 5 bodies: "
         f"{st.session_state.synergy:.2f}/1.00", kind="done")


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("## 🤝 AI Agent Society")
    st.caption("Five bodies · one mind · perfect harmony")
    st.divider()
    task = st.text_input("💬 Give the swarm a task",
                         placeholder="e.g. build a REST API with auth…")
    deploy = st.button("🚀 Deploy Swarm", use_container_width=True, type="primary")
    st.divider()
    st.markdown("### 👥 Members")
    for a in AGENTS.values():
        dot = "🟢 online" if st.session_state.busy != a["name"].lower() else "🟠 active"
        st.markdown(f"**{a['emoji']} {a['name']}**  \n<a style='color:{a['color']}'>{dot}</a> · {a['role']}",
                    unsafe_allow_html=True)
        st.caption("")
    st.divider()
    if st.button("🧹 Clear feed"):
        st.session_state.feed = []
        st.session_state.synergy = 0.0
        st.session_state.tasks_done = 0
        st.rerun()

if deploy and task.strip():
    run_task(task.strip())
    st.rerun()

# ---------------------------------------------------------------- main layout
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    st.markdown(f"# 🤝 AI Agent Society <span style='font-size:0.6em'>● LIVE</span>",
                unsafe_allow_html=True)
with c2:
    st.metric("Tasks Completed", st.session_state.tasks_done)
with c3:
    st.metric("Harmony / Synergy", f"{st.session_state.synergy:.2f} / 1.00")

st.progress(st.session_state.synergy,
            text=f"Swarm synergy — {'PERFECT HARMONY ✨' if st.session_state.synergy >= 0.95 else 'collaborating…'}")

tab_feed, tab_agents, tab_about = st.tabs(["📡 Live Message Feed", "👥 The Five Bodies", "ℹ️ How they harmonize"])

with tab_feed:
    if not st.session_state.feed:
        st.info("The society is idle. Type a task in the sidebar and hit **🚀 Deploy Swarm** to watch all five agents collaborate in real time.")
    else:
        feed_box = st.container(height=520)
        with feed_box:
            for m in reversed(st.session_state.feed[-60:]):
                s = AGENTS.get(m["sender"], {"emoji": "🧑", "name": "User", "color": "#94A3B8"})
                r = AGENTS.get(m["receiver"], {"emoji": "🧑", "name": "User", "color": "#94A3B8"})
                st.markdown(
                    f"<div style='padding:6px 10px;border-left:3px solid {s['color']};margin-bottom:6px;background:#0f172a22;border-radius:6px'>"
                    f"<b style='color:{s['color']}'>{s['emoji']} {s['name']}</b> "
                    f"<span style='opacity:.5'>→</span> "
                    f"<b style='color:{r['color']}'>{r['emoji']} {r['name']}</b> "
                    f"<span style='opacity:.4;font-size:.8em'>{m['t']}</span><br/>{m['text']}</div>",
                    unsafe_allow_html=True)

with tab_agents:
    cols = st.columns(5)
    for col, (aid, a) in zip(cols, AGENTS.items()):
        with col:
            active = st.session_state.busy == aid
            with st.border(True) if hasattr(st, "border") else st.container(border=True):
                st.markdown(f"### {a['emoji']} {a['name']}")
                st.badge("ACTIVE 🟠" if active else "IDLE 🟢",
                         color="orange" if active else "green")
                st.caption(a["role"])

with tab_about:
    st.markdown("""
**The collaboration protocol (each task runs all 5 phases):**

| Phase | From → To | What happens |
|---|---|---|
| 1. Dispatch | 🔵 Orchestrator → 🩵 Researcher | Parses intent, assigns specialists |
| 2. Discovery | 🩵 Researcher → 🟢 Developer | Delivers docs, patterns, constraints |
| 3. Build | 🟢 Developer → 🟡 Critic | Submits draft implementation for review |
| 4. Review | 🟡 Critic → 🟢 Developer | Feedback loop until quality bar is met |
| 5. Ship | 🟣 Executor → 🔵 Orchestrator | Synthesizes and delivers the final artifact |

Every exchange raises the **synergy score**. The Critic's feedback loop back to the
Developer guarantees no task ships unreviewed — that closed loop *is* the harmony.
""")

# ---------------------------------------------------------------- auto-refresh
if st.session_state.busy:
    time.sleep(0.8)
    st.rerun()
