"""
🤝 SYNERGYMESH — AI Agent Society (robust Streamlit build)

Five-body agent society (Orchestrator 🔵 · Researcher 🩵 · Developer 🟢 ·
Critic 🟡 · Executor 🟣) with a full user interface AND a chat interface.

Hardening applied (fixes blank/crash pages on Streamlit Cloud):
  1. Lazy-load / session-state init — nothing heavy runs at import time;
     the society boots only when the user clicks "Initialize Agent Society".
  2. Safe async loop management — any coroutine is run on a dedicated
     event loop inside a worker thread, never colliding with Streamlit's
     main-thread loop.
  3. Try/except error boundaries — every risky block surfaces errors in
     the UI via st.error + traceback instead of crashing to a blank page.
  4. Environment & dependency checks — module/API-key/config validation
     with visible fallback warnings before anything else renders.

Run locally:  streamlit run streamlit_app_v2.py
Deploy free:  https://share.streamlit.io
"""

import asyncio
import importlib
import os
import threading
import time
import traceback
from datetime import datetime

import streamlit as st

# ============================================================ 4. ENVIRONMENT CHECKS
REQUIRED_MODULES = ["asyncio", "json", "random", "re", "threading"]
OPTIONAL_LLM_KEYS = {
    "OPENAI_API_KEY": "optional — enables real LLM replies from the agents",
    "ANTHROPIC_API_KEY": "optional — enables Claude-backed agents",
}


def check_environment() -> dict:
    """Validate interpreter, modules and API keys. Never raises."""
    report = {"python_ok": True, "missing": [], "keys_found": [], "keys_missing": []}
    try:
        if not (3, 9) <= tuple(__import__("sys").version_info[:2]):
            report["python_ok"] = False
        for m in REQUIRED_MODULES:
            try:
                importlib.import_module(m)
            except Exception:
                report["missing"].append(m)
        for key, desc in OPTIONAL_LLM_KEYS.items():
            (report["keys_found"] if os.environ.get(key) else report["keys_missing"]).append((key, desc))
    except Exception:
        # environment check itself must never crash the app
        report["python_ok"] = report["python_ok"] or True
    return report


# ============================================================ 1. LAZY LOADING
@st.cache_resource(show_spinner=False)
def load_engine():
    """Import the society engine only when explicitly requested (lazy)."""
    import society_engine  # noqa: WPS433
    return society_engine


def initialize_society():
    """Boot the agent society once, store it in session state."""
    engine = load_engine()
    st.session_state.society = engine          # shared engine handle
    st.session_state.initialized = True
    st.session_state.chat = []
    st.session_state.feed = []
    st.session_state.tasks_done = 0
    st.session_state.busy = False
    st.session_state.last_error = None


# ============================================================ 2. SAFE ASYNC LOOP
def run_coro_safely(coro_factory):
    """
    Run an async workload WITHOUT touching Streamlit's main-thread loop.

    A brand-new event loop is created inside a dedicated worker thread, so
    we never call asyncio.run() on a loop that already exists (the classic
    'cannot be called from a running event loop' crash), and we always
    close the loop afterwards. Returns (result, error).
    """
    result, error = None, None

    def _worker():
        nonlocal result, error
        loop = None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(coro_factory())
        except Exception as exc:                       # noqa: BLE001
            error = f"{type(exc).__name__}: {exc}"
        finally:
            if loop is not None:
                try:
                    loop.run_until_complete(loop.shutdown_asyncgens())
                except Exception:
                    pass
                loop.close()

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    thread.join(timeout=120)
    if thread.is_alive():
        return None, "Agent workload timed out after 120s."
    return result, error


async def _collect_events_async(engine, task: str, seed: int):
    """Async wrapper around the (sync) generator engine — demonstrates safe
    async usage while staying compatible with LLM SDKs later."""
    events = []
    for ev in engine.run_society(task, seed=seed):
        await asyncio.sleep(0)          # cooperative yield point
        events.append(ev)
    return events


def execute_mission(task: str, seed: int):
    """
    Run one full society cycle.

    If an event loop is already running on this thread (some Streamlit Cloud
    runtimes do this), we cannot nest loops safely — so we fall back to the
    synchronous generator. Otherwise we use the dedicated-loop worker thread.
    Returns (events, error_message_or_None).
    """
    engine = st.session_state.society
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No loop here -> safe to use our private loop in a worker thread
        return run_coro_safely(lambda: _collect_events_async(engine, task, seed))
    # Loop already active -> sync fallback (engine is pure-Python/synchronous)
    try:
        return list(engine.run_society(task, seed=seed)), None
    except Exception as exc:                   # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"


# ============================================================ 3. ERROR BOUNDARY
def show_error_boundary(exc_obj=None, message=""):
    """Render any exception directly in the UI instead of a blank page."""
    msg = message or (traceback.format_exception_only(type(exc_obj), exc_obj)[0]
                      if exc_obj else "Unknown error")
    st.error(f"⚠️ **Runtime error caught (app kept running):** {msg}")
    if exc_obj is not None:
        with st.expander("🐞 Full traceback (click to expand)", expanded=False):
            st.code("".join(traceback.format_exception(exc_obj)), language="text")


# ============================================================ PAGE SETUP (cheap)
st.set_page_config(
    page_title="SynergyMesh — AI Agent Society",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

try:  # st.context exists only on newer Streamlit — guard it
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

# ---- minimal defaults only; NO heavy work at top level -----------------
st.session_state.setdefault("initialized", False)
st.session_state.setdefault("last_error", None)

if st.session_state.last_error:
    st.error(f"⚠️ Last run raised an error: {st.session_state.last_error}")

env = check_environment()

st.markdown("## 🤝 SynergyMesh — AI Agent Society")
st.caption("Five bodies. One mind. Perfect harmony.")

# ============================================================ BOOT SCREEN (lazy init)
if not st.session_state.initialized:
    if env["missing"]:
        st.warning(
            "🔎 Some optional modules are missing: "
            + ", ".join(env["missing"])
            + " — the society will boot in fallback mode."
        )
    if env["keys_missing"]:
        st.info(
            "💡 No LLM API keys detected ("
            + ", ".join(k for k, _ in env["keys_missing"])
            + "). That's fine — the society runs its built-in simulated swarm. "
            "Add a key in Streamlit Cloud → Settings → Secrets to enable live model calls."
        )
    if not env["python_ok"]:
        st.warning("⚠️ Python ≥ 3.9 recommended. The app will still attempt to run.")

    st.markdown(
        "**The agent society is not loaded yet.** Page rendering is instant because "
        "engine initialization is deferred until you press the button below."
    )
    if st.button("🚀 Initialize Agent Society", type="primary", use_container_width=True):
        try:
            with st.spinner("Booting Orchestrator, Researcher, Developer, Critic & Executor…"):
                initialize_society()
            st.rerun()
        except Exception as e:  # noqa: BLE001
            st.session_state.last_error = f"{type(e).__name__}: {e}"
            show_error_boundary(e)
    st.stop()

# ============================================================ MAIN APP
AGENTS = st.session_state.society.AGENTS


def now_str() -> str:
    return datetime.now().strftime("%H:%M:%S")


def push_feed(agent_key: str, text: str):
    st.session_state.feed.append({"time": now_str(), "agent": agent_key, "text": text})


# ---- header metrics ----------------------------------------------------
m1, m2, m3 = st.columns([1, 1, 2])
tasks = st.session_state.tasks_done
synergy = round(min(0.98, 0.60 + tasks * 0.06), 2)
m1.metric("Tasks Completed", tasks)
m2.metric("Messages Exchanged", len(st.session_state.feed))
m3.metric("Harmony / Synergy", f"{synergy:.2f} / 1.00")
st.progress(min(synergy, 1.0),
            text="PERFECT HARMONY ✨" if synergy >= 0.95 else "Collaborative resonance")

# ---- sidebar roster -----------------------------------------------------
with st.sidebar:
    st.header("👥 The Five Bodies")
    for key, a in AGENTS.items():
        status = "🟢 online"
        st.markdown(
            f'<span class="agent-badge" style="background:{a["color"]}">'
            f'{a["emoji"]} {a["name"]}</span>&nbsp;<small>{a["role"]} · {status}</small>',
            unsafe_allow_html=True,
        )
        st.write("")
    st.divider()
    st.caption(f"Engine: `society_engine.py` · Async bridge: `run_coro_safely()` · "
               f"LLM keys: {len(env['keys_found'])} found")
    if st.button("🧹 Reset society", use_container_width=True):
        st.session_state.chat = []
        st.session_state.feed = []
        st.session_state.tasks_done = 0
        st.session_state.busy = False
        st.rerun()
    if st.button("⏻ Shutdown & un-initialize", use_container_width=True):
        st.session_state.initialized = False
        st.rerun()

# ---- tabs ----------------------------------------------------------------
tab_chat, tab_feed, tab_about = st.tabs(
    ["💬 Chat with the Society", "📡 Live Message Feed", "ℹ️ How it works"]
)

# ============================================================== CHAT INTERFACE
with tab_chat:
    try:
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

        # -- process a queued mission safely (async bridge + error boundary)
        if st.session_state.busy:
            task = st.session_state.chat[-1]["content"]
            with st.spinner("The swarm is collaborating on your request…"):
                events, err = execute_mission(task, seed=st.session_state.tasks_done)
            if err:
                st.session_state.busy = False
                st.session_state.last_error = err
                show_error_boundary(message=err)
                st.session_state.chat.append(
                    {"role": "agent", "agent": "executor",
                     "content": "⚠️ The swarm hit an internal fault and recovered gracefully. "
                                "Please retry the mission."}
                )
                st.rerun()
            else:
                for ev in events:
                    push_feed(ev["agent"], ev["text"])
                st.session_state.chat.append(
                    {"role": "agent", "agent": "executor", "content": events[-1]["text"]}
                )
                st.session_state.tasks_done += 1
                st.session_state.busy = False
                time.sleep(0.05)
                st.rerun()

        # -- quick-suggestion chips
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
    except Exception as e:  # noqa: BLE001
        st.session_state.busy = False
        show_error_boundary(e, message=f"Chat tab crashed: {type(e).__name__}: {e}")

# ============================================================== LIVE FEED
with tab_feed:
    try:
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
    except Exception as e:  # noqa: BLE001
        show_error_boundary(e, message=f"Feed tab crashed: {type(e).__name__}: {e}")

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

        ### 🛡️ Stability architecture
        - **Lazy init:** engine loads only after you press *Initialize Agent Society*
        - **Safe async:** agent work runs on a private event loop in a worker thread
        - **Error boundaries:** crashes render inline with tracebacks, never blank pages
        - **Env checks:** missing modules / API keys surface as warnings, not failures
        """
    )
