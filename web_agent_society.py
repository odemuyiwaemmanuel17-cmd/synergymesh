#!/usr/bin/env python3
"""
LIVE AI AGENT SOCIETY - WEB SERVER
----------------------------------
Serves an interactive web dashboard for the 5-agent society on localhost.

Run:  python3 web_agent_society.py
Open: http://localhost:8000
"""

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# ------------------------- Agent Society Core -------------------------

class AgentSociety:
    def __init__(self):
        self.messages = []       # chat/log history
        self.tasks_done = 0
        self.synergy = 0.10
        self.lock = threading.Lock()
        self.running = True

    def log(self, agent, color, text):
        with self.lock:
            self.messages.append({
                "agent": agent,
                "color": color,
                "text": text,
                "time": time.strftime("%H:%M:%S"),
            })

    def process_task(self, task):
        """Simulate the 5 agents collaborating on a task."""
        self.log("SYSTEM", "white", f"New task received: \"{task}\"")
        time.sleep(0.4)

        self.log("ORCHESTRATOR", "blue",
                 f"Analyzing intent of '{task}'. Delegating to swarm...")
        time.sleep(0.5)

        self.log("RESEARCHER", "cyan",
                 "Scanning knowledge base for relevant patterns and docs...")
        time.sleep(0.5)
        self.log("RESEARCHER", "cyan",
                 "Context gathered: best practices + prior art compiled.")
        time.sleep(0.4)

        self.log("DEVELOPER", "green",
                 "Drafting solution architecture and implementation...")
        time.sleep(0.6)
        self.log("DEVELOPER", "green",
                 "Prototype ready. Handing off for review.")
        time.sleep(0.4)

        self.log("CRITIC", "yellow",
                 "Reviewing for logic gaps, edge cases, security...")
        time.sleep(0.5)
        self.log("CRITIC", "yellow",
                 "Approved. Minor suggestion: add error handling. ✓")
        time.sleep(0.4)

        self.log("EXECUTOR", "magenta",
                 f"Synthesizing final deliverable for: {task}")
        time.sleep(0.5)
        self.log("EXECUTOR", "magenta",
                 "Task complete. Solution delivered to user. ✅")

        with self.lock:
            self.tasks_done += 1
            self.synergy = min(1.0, round(self.synergy + 0.18, 2))

        return {
            "status": "complete",
            "tasks_done": self.tasks_done,
            "synergy": self.synergy,
        }


SOCIETY = AgentSociety()


def background_demo():
    """Auto-run one demo task at startup so the dashboard feels alive."""
    time.sleep(1.0)
    SOCIETY.process_task("create a python script that calculates fibonacci numbers")


# ------------------------- Web Server -------------------------

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>🤖 AI Agent Society — Live</title>
<style>
  :root { --bg:#0d1117; --panel:#161b22; --border:#30363d; --text:#e6edf3; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background:var(--bg); color:var(--text); font-family:'Segoe UI',monospace; }
  header { padding:18px 24px; background:var(--panel); border-bottom:1px solid var(--border);
           display:flex; justify-content:space-between; align-items:center; }
  h1 { font-size:1.3rem; }
  .stats { display:flex; gap:16px; font-size:.9rem; }
  .stat { background:#21262d; padding:6px 14px; border-radius:20px; border:1px solid var(--border);}
  main { display:grid; grid-template-columns: 260px 1fr; gap:16px; padding:16px; height:calc(100vh - 180px); }
  .agents { background:var(--panel); border:1px solid var(--border); border-radius:10px; padding:14px; }
  .agent { display:flex; align-items:center; gap:10px; padding:10px 8px; border-radius:8px; margin-bottom:6px;}
  .dot { width:10px; height:10px; border-radius:50%; animation:pulse 1.6s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
  .feed-wrap { background:var(--panel); border:1px solid var(--border); border-radius:10px;
               display:flex; flex-direction:column; overflow:hidden; }
  #feed { flex:1; overflow-y:auto; padding:16px; font-size:.88rem; line-height:1.7; }
  .msg { margin-bottom:4px; }
  .tag { font-weight:bold; margin-right:8px; }
  .t { color:#8b949e; font-size:.75rem; margin-right:8px; }
  .c-blue{color:#58a6ff}.c-cyan{color:#39d2c0}.c-green{color:#3fb950}
  .c-yellow{color:#d29922}.c-magenta{color:#bc8cff}.c-white{color:#e6edf3}
  footer { padding:14px 16px; background:var(--panel); border-top:1px solid var(--border); display:flex; gap:10px; }
  input { flex:1; background:#0d1117; border:1px solid var(--border); color:var(--text);
          padding:12px 16px; border-radius:8px; font-size:.95rem; outline:none; }
  input:focus { border-color:#58a6ff; }
  button { background:#238636; color:white; border:none; padding:12px 26px; border-radius:8px;
           cursor:pointer; font-weight:bold; font-size:.95rem; }
  button:hover { background:#2ea043; }
  .bar { height:8px; background:#21262d; border-radius:4px; margin-top:10px; overflow:hidden;}
  .fill { height:100%; background:linear-gradient(90deg,#bc8cff,#3fb950); transition:width .8s;}
</style>
</head>
<body>
<header>
  <h1>🤖 AI Agent Society <span style="font-size:.8rem;color:#3fb950">● LIVE</span></h1>
  <div class="stats">
    <div class="stat">Tasks: <b id="tasks">0</b></div>
    <div class="stat">Synergy: <b id="syn">0.10</b>/1.00</div>
  </div>
</header>
<main>
  <div class="agents">
    <b style="font-size:.85rem;color:#8b949e">MEMBERS ONLINE</b><br><br>
    <div class="agent"><span class="dot" style="background:#58a6ff"></span>Orchestrator</div>
    <div class="agent"><span class="dot" style="background:#39d2c0"></span>Researcher</div>
    <div class="agent"><span class="dot" style="background:#3fb950"></span>Developer</div>
    <div class="agent"><span class="dot" style="background:#d29922"></span>Critic</div>
    <div class="agent"><span class="dot" style="background:#bc8cff"></span>Executor (You)</div>
    <div style="margin-top:18px;font-size:.8rem;color:#8b949e">Harmony meter</div>
    <div class="bar"><div class="fill" id="fill" style="width:10%"></div></div>
  </div>
  <div class="feed-wrap"><div id="feed"></div></div>
</main>
<footer>
  <input id="task" placeholder="Give the society a task... e.g. build a web scraper" />
  <button onclick="submitTask()">Deploy Swarm 🚀</button>
</footer>
<script>
let lastIdx = 0;
async function poll() {
  try {
    const r = await fetch('/api/state');
    const s = await r.json();
    const feed = document.getElementById('feed');
    s.messages.slice(lastIdx).forEach(m => {
      const d = document.createElement('div');
      d.className = 'msg';
      d.innerHTML = `<span class="t">${m.time}</span><span class="tag c-${m.color}">[${m.agent}]</span><span class="c-${m.color}">${m.text}</span>`;
      feed.appendChild(d);
    });
    if (s.messages.length > lastIdx) feed.scrollTop = feed.scrollHeight;
    lastIdx = s.messages.length;
    document.getElementById('tasks').textContent = s.tasks_done;
    document.getElementById('syn').textContent = s.synergy.toFixed(2);
    document.getElementById('fill').style.width = (s.synergy*100)+'%';
  } catch(e) {}
}
async function submitTask() {
  const inp = document.getElementById('task');
  const t = inp.value.trim();
  if (!t) return;
  inp.value = '';
  await fetch('/api/task', {method:'POST', headers:{'Content-Type':'application/json'},
                            body: JSON.stringify({task:t})});
}
document.getElementById('task').addEventListener('keydown', e => {
  if (e.key === 'Enter') submitTask();
});
setInterval(poll, 700);
poll();
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self._send(200, PAGE.encode(), "text/html")
        elif self.path == "/api/state":
            with SOCIETY.lock:
                state = {
                    "messages": SOCIETY.messages,
                    "tasks_done": SOCIETY.tasks_done,
                    "synergy": SOCIETY.synergy,
                }
            self._send(200, json.dumps(state).encode())
        else:
            self._send(404, b'{"error":"not found"}')

    def do_POST(self):
        if self.path == "/api/task":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b'{"task":"unnamed"}')
            task = data.get("task", "unnamed task")
            # process in a thread so the HTTP response returns fast
            threading.Thread(target=SOCIETY.process_task, args=(task,), daemon=True).start()
            self._send(200, json.dumps({"status": "accepted", "task": task}).encode())
        else:
            self._send(404, b'{"error":"not found"}')


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


if __name__ == "__main__":
    PORT = 8000
    server = ThreadedHTTPServer(("0.0.0.0", PORT), Handler)
    threading.Thread(target=background_demo, daemon=True).start()
    print(f"🌐 AI Agent Society is LIVE at http://localhost:{PORT}")
    print("   Press Ctrl+C to shut down the society.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Society disbanded. Goodbye!")
