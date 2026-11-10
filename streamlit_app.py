"""
🤝 SYNERGYMESH — AI Agent Society
A five-body agent society (Orchestrator 🔵 · Researcher 🩵 · Developer 🟢 ·
Critic 🟡 · Executor 🟣) with a full user interface AND a chat interface.

Run locally:  streamlit run streamlit_app.py
Deploy free:  https://share.streamlit.io
"""

import time
from datetime import datetime

import streamlit as st

from society_engine import AGENTS, run_society, synergy_for

# ---------------------------------------------------------------- page setup
st.set_page_config(
    page_title="SynergyMesh — AI Agent Society",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:
    st.context.configure(
        theme={
            "base": "light",
            "primaryColor": "#4C7DF0",
            "backgroundColor": "#FFFFFF",
            "secondaryBackgroundColor": "#F1F5F9",
            "textColor": "#0F172A",
        }
    )
except Exception:
    pass

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.2rem;}
    div[data-testid="stChatMessage"] {border-radius: 12px; padding: .4rem .6rem;}
    .agent-badge {display:inline-block;padding:2px 10px;border-radius:999px;
                  color:#fff;font-size:.8rem;font-weight:600;margin-right:6px;}
    .stTabs [data-baseweb="tab-list"] {gap: 6px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- session state
defaults = dict(
    chat=[],          # [{"role": "user"/"agent", "agent": key|None, "content": str}]
    feed=[],          # [{"time": str, "agent": key, "text": str}]
    tasks_done=0,
    busy=False,
)
for k, v in defaults.items():
    st.session_state.setdefault(k, v)


def now() -> str:
    return datetime.now().strftime("%H:%M:%S")


def push_feed(agent_key: str, text: str):
    st.session_state.feed.append({"time": now(), "agent": agent_key, "text": text})


# ---------------------------------------------------------------- header + metrics
st.markdown("## 🤝 SynergyMesh — AI Agent Society")
st.caption("Five bodies. One mind. Perfect harmony.")

m1, m2, m3 = st.columns([1, 1, 2])
tasks = st.session_state.tasks_done
synergy = synergy_for(tasks)
m1.metric("Tasks Completed", tasks)
m2.metric("Messages Exchanged", len(st.session_state.feed))
m3.metric("Harmony / Synergy", f"{synergy:.2f} / 1.00")
st.progress(min(synergy, 1.0),
            text="PERFECT HARMONY ✨" if synergy >= 0.95 else "Collaborative resonance")

# ---------------------------------------------------------------- sidebar roster
with st.sidebar:
    st.header("👥 The Five Bodies")
    for key, a in AGENTS.items():
        st.markdown(
            f'<span class="agent-badge" style="background:{a["color"]}">'
            f'{a["emoji"]} {a["name"]}</span>&nbsp;<small>{a["role"]}</small>',
            unsafe_allow_html=True,
        )
        st.write("")
    st.divider()
    if st.button("🧹 Reset society", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = [] if isinstance(v, list) else 0 if isinstance(v, int) else v
        st.rerun()

# ---------------------------------------------------------------- tabs
tab_chat, tab_feed, tab_about = st.tabs(["💬 Chat with the Society", "📡 Live Message Feed", "ℹ️ How it works"])

# ============================================================== CHAT INTERFACE
with tab_chat:
    # render history
    for msg in st.session_state.chat:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            a = AGENTS[msg["agent"]]
            with st.chat_message("assistant", avatar=a["emoji"]):
                st.markdown(
                    f'**<span class="agent-badge" style="background:{a["color"]}">'
                    f'{a["name"]}</span>**  \n{msg["content"]}',
                    unsafe_allow_html=True,
                )

    if st.session_state.busy:
        with st.spinner("The swarm is collaborating on your request…"):
            task = st.session_state.chat[-1]["content"]
            events = list(run_society(task, seed=tasks))
            time.sleep(0.05)

            # record everything, then release the lock and rerun cleanly
            for ev in events:
                push_feed(ev["agent"], ev["text"])
            st.session_state.chat.append(
                {"role": "agent", "agent": "executor", "content": events[-1]["text"]}
            )
            st.session_state.tasks_done += 1
            st.session_state.busy = False
            st.rerun()

    # quick-suggestion chips
    c1, c2, c3, c4 = st.columns(4)
    suggestions = {
        c1: "Build a REST API for a todo app",
        c2: "Research the best vector database",
        c3: "Review my authentication flow",
        c4: "Create a fibonacci script",
    }
    picked = None
    for col, s in suggestions.items():
        if col.button(f"💡 {s}", use_container_width=True, key=f"sug_{s}"):
            picked = s

    prompt = st.chat_input("Ask the society anything, or give it a mission…")
    user_msg = prompt or picked

    if user_msg:
        st.session_state.chat.append({"role": "user", "agent": None, "content": user_msg})
        st.session_state.busy = True
        st.rerun()

# ============================================================== LIVE FEED
with tab_feed:
    st.subheader("📡 Inter-agent message stream")
    if not st.session_state.feed:
        st.info("No messages yet — send the society a mission in the 💬 Chat tab.")
    else:
        for row in reversed(st.session_state.feed[-200:]):
            a = AGENTS[row["agent"]]
            st.markdown(
                f'<code style="color:#64748B">{row["time"]}</code>&nbsp;'
                f'<span class="agent-badge" style="background:{a["color"]}">'
                f'{a["emoji"]} {a["name"]}</span>&nbsp;{row["text"]}',
                unsafe_allow_html=True,
            )

# ============================================================== ABOUT
with tab_about:
    st.subheader("🎼 The collaboration protocol")
    st.markdown(
        """
        | Phase | Body | Contribution |
        |-------|------|--------------|
        | 1 · Dispatch | 🔵 Orchestrator | Parses your request, routes to the right lead specialist |
        | 2 · Discovery | 🩵 Researcher | Gathers context, docs and best practices |
        | 3 · Build | 🟢 Developer | Implements the solution with tests & error handling |
        | 4 · Review | 🟡 Critic | Audits quality; can bounce work back for revisions |
        | 5 · Ship | 🟣 Executor | Synthesizes and delivers the final artifact |

        Every mission passes through all five bodies — that's what keeps the
        **harmony score** climbing. Ask follow-ups in the chat and the swarm iterates.
        """
    )
