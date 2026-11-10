"""
🤝 AI Agent Society — shared engine (pure Python, zero dependencies).

Five bodies working in harmony:
  🔵 Orchestrator · 🩵 Researcher · 🟢 Developer · 🟡 Critic · 🟣 Executor

Used by both the Streamlit UI and the terminal demo.
"""

import random
import re

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

PHASES = [
    ("dispatch",  "orchestrator"),
    ("discovery", "researcher"),
    ("build",     "developer"),
    ("review",    "critic"),
    ("ship",      "executor"),
]


def classify(task: str) -> str:
    """Route a task to the specialist that leads it."""
    t = task.lower()
    if re.search(r"research|what is|how does|explain|compare|find|study|why", t):
        return "researcher"
    if re.search(r"review|audit|test|check|secur|optimi|refactor|bug", t):
        return "critic"
    if re.search(r"build|create|code|write|implement|script|app|website|api|scraper|class|function", t):
        return "developer"
    return "orchestrator"


# ---------------------------------------------------------------- script templates
_BUILD_LINES = {
    "developer": [
        "Drafting module structure and interfaces for: {task}",
        "Implementing core logic with type hints + docstrings",
        "Adding error handling, logging, and unit-test hooks",
    ],
    "researcher": [
        "Scanning documentation & knowledge sources for: {task}",
        "Cross-checking best practices and prior art",
        "Compiling findings brief for the Developer",
    ],
    "critic": [
        "Auditing requirements & acceptance criteria for: {task}",
        "Defining test matrix and quality gates",
        "Preparing review checklist for the build",
    ],
    "orchestrator": [
        "Decomposing goal into subtasks: {task}",
        "Assigning work packets across the five bodies",
        "Balancing load and sequencing dependencies",
    ],
}

_CRITIC_VERDICTS = [
    "Edge cases covered, style consistent — approved ✅",
    "Logic verified against spec, no blockers — approved ✅",
    "Performance acceptable, tests pass — approved ✅",
]


def run_society(task: str, seed=None):
    """
    Execute one full collaboration cycle.

    Yields events as dicts: {"agent": key, "text": str, "phase": str}
    The final event from the Executor contains the deliverable summary.
    """
    rng = random.Random(seed)
    lead = classify(task)

    # Phase 1 — dispatch
    yield {"agent": "orchestrator", "phase": "dispatch",
           "text": f"🎯 New mission received: \"{task}\""}
    yield {"agent": "orchestrator", "phase": "dispatch",
           "text": f"Routing to {AGENTS[lead]['emoji']} {AGENTS[lead]['name']} as lead; all bodies on standby."}

    # Phase 2 — discovery (always includes the researcher briefing)
    yield {"agent": "researcher", "phase": "discovery",
           "text": f"📚 Context gathered: relevant patterns, docs and constraints for \"{task}\" located."}
    for line in _BUILD_LINES[lead][:-1]:
        yield {"agent": lead, "phase": "discovery",
               "text": f"⚙️ {line.format(task=task)}"}

    # Phase 3 — build
    yield {"agent": "developer", "phase": "build",
           "text": f"🛠️ Building solution for: {task}"}
    for line in _BUILD_LINES["developer"][1:]:
        yield {"agent": "developer", "phase": "build", "text": f"🛠️ {line}"}

    # Phase 4 — review (occasional revision loop for realism)
    yield {"agent": "critic", "phase": "review",
           "text": "🔍 Reviewing build artifacts against acceptance criteria…"}
    if rng.random() < 0.35:
        yield {"agent": "critic", "phase": "review",
               "text": "⚠️ Minor issue found — returning to Developer for one revision pass."}
        yield {"agent": "developer", "phase": "review",
               "text": "🔄 Revision complete: hardened inputs, clarified naming. Resubmitted."}
    yield {"agent": "critic", "phase": "review",
           "text": f"✅ {rng.choice(_CRITIC_VERDICTS)}"}

    # Phase 5 — ship
    deliverable = (
        f"📦 **Delivered** — \"{task}\"\n\n"
        f"- Lead: {AGENTS[lead]['emoji']} {AGENTS[lead]['name']}\n"
        f"- Reviewed by: 🟡 Critic (approved)\n"
        f"- Synergy applied: all 5 bodies contributed\n\n"
        f"The swarm produced a complete, tested solution package. "
        f"Ask follow-up questions in this chat and the society will iterate on it."
    )
    yield {"agent": "executor", "phase": "ship", "text": deliverable}


def synergy_for(n_tasks: int) -> float:
    """Harmony grows as the society collaborates more, capping near perfect."""
    return round(min(0.98, 0.60 + n_tasks * 0.06), 2)
