"""AERQEN web chat server (ADR-013). Standard library only.

Run it:

    python -m app.web.server

It prints a link for this PC and a link for your phone (same WiFi). Open either in a
browser and chat with the agent. MEDIUM-risk steps ask for Allow/Deny right in the page.

Security: the server binds to the LAN so a phone can reach it, so it requires a token
(printed inside the link). Without the token every request is refused. This is a local
tool for the owner, not a public website.
"""

from __future__ import annotations

import json
import secrets
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

if __package__ in (None, ""):
    sys.path.insert(0, ".")

from app.configuration.settings import load_settings
from app.entrypoint.cli import build_agent
from app.web.service import AgentService
from security.audit.log import JsonlAuditLog

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>AERQEN</title>
<style>
  :root { --bg:#0e1116; --panel:#171b22; --me:#2563eb; --bot:#232a34; --txt:#e6e9ef;
          --muted:#9aa4b2; --warn:#b45309; --ok:#15803d; }
  * { box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
  html,body { margin:0; height:100%; background:var(--bg); color:var(--txt);
              font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }
  #app { display:flex; flex-direction:column; height:100dvh; max-width:760px; margin:0 auto; }
  header { padding:14px 16px; font-weight:700; font-size:18px; border-bottom:1px solid #222938;
           display:flex; align-items:center; gap:8px; }
  header .dot { width:10px; height:10px; border-radius:50%; background:var(--ok); }
  #log { flex:1; overflow-y:auto; padding:16px; display:flex; flex-direction:column; gap:10px; }
  .msg { max-width:85%; padding:10px 13px; border-radius:14px; line-height:1.4; white-space:pre-wrap;
         word-wrap:break-word; }
  .me  { align-self:flex-end; background:var(--me); border-bottom-right-radius:4px; }
  .bot { align-self:flex-start; background:var(--bot); border-bottom-left-radius:4px; }
  .sys { align-self:center; color:var(--muted); font-size:13px; background:transparent; }
  .card { align-self:flex-start; background:var(--panel); border:1px solid #2b3342; border-radius:14px;
          padding:12px; max-width:92%; }
  .card .t { color:var(--warn); font-weight:700; margin-bottom:6px; }
  .card code { background:#0b0e13; padding:2px 6px; border-radius:6px; font-size:13px; }
  .card .btns { margin-top:10px; display:flex; gap:10px; }
  button { border:0; border-radius:10px; padding:10px 16px; font-size:15px; font-weight:600;
           color:#fff; cursor:pointer; }
  .allow { background:var(--ok); } .deny { background:#b91c1c; }
  form { display:flex; gap:8px; padding:12px; border-top:1px solid #222938; }
  input { flex:1; padding:13px 14px; border-radius:12px; border:1px solid #2b3342; background:#0b0e13;
          color:var(--txt); font-size:16px; }
  .send { background:var(--me); }
  .typing { color:var(--muted); font-size:13px; align-self:flex-start; }
</style>
</head>
<body>
<div id="app">
  <header><span class="dot"></span> AERQEN</header>
  <div id="log">
    <div class="msg sys">Hi! Main AERQEN hoon. Kuch bhi likho — files banau, yaad rakhu, ya sawaal ka jawab du.</div>
  </div>
  <form id="f">
    <input id="m" autocomplete="off" placeholder="Type a message…" />
    <button class="send" type="submit">Send</button>
  </form>
</div>
<script>
const TOKEN = new URLSearchParams(location.search).get("t") || "";
const log = document.getElementById("log");
const form = document.getElementById("f");
const input = document.getElementById("m");

function add(cls, text){ const d=document.createElement("div"); d.className="msg "+cls; d.textContent=text; log.appendChild(d); log.scrollTop=log.scrollHeight; return d; }
function api(path, body){ return fetch(path, {method:"POST", headers:{"Content-Type":"application/json","X-AERQEN-Token":TOKEN}, body:JSON.stringify(body)}).then(r=>r.json()); }
function get(path){ return fetch(path, {headers:{"X-AERQEN-Token":TOKEN}}).then(r=>r.json()); }

let busy=false;
form.addEventListener("submit", async (e)=>{
  e.preventDefault();
  const text=input.value.trim(); if(!text||busy) return;
  busy=true; input.value="";
  add("me", text);
  const typing=document.createElement("div"); typing.className="typing"; typing.textContent="AERQEN soch raha hai…"; log.appendChild(typing); log.scrollTop=log.scrollHeight;
  let sid;
  try { const r=await api("/api/ask",{message:text}); sid=r.task_id; } catch(err){ typing.remove(); add("sys","Connection error."); busy=false; return; }
  let approvalShown=false, card=null;
  const poll=async()=>{
    let s; try { s=await get("/api/poll?task_id="+sid); } catch(e){ setTimeout(poll,1200); return; }
    if(s.state==="awaiting_approval"){
      if(!approvalShown){
        approvalShown=true; typing.remove();
        card=document.createElement("div"); card.className="card";
        const p=s.pending||{};
        card.innerHTML='<div class="t">Approval needed</div><div>Tool: <code>'+(p.tool||"")+'</code></div><div>Risk: <code>'+(p.risk||"")+'</code></div><div style="margin-top:4px">Input: <code>'+escapeHtml(JSON.stringify(p.input||{}))+'</code></div>';
        const btns=document.createElement("div"); btns.className="btns";
        const yes=document.createElement("button"); yes.className="allow"; yes.textContent="Allow";
        const no=document.createElement("button"); no.className="deny"; no.textContent="Deny";
        yes.onclick=()=>decide(true); no.onclick=()=>decide(false);
        btns.appendChild(yes); btns.appendChild(no); card.appendChild(btns);
        log.appendChild(card); log.scrollTop=log.scrollHeight;
      }
      setTimeout(poll,1000); return;
    }
    if(s.state==="running"){ setTimeout(poll,1000); return; }
    // finished
    typing.remove(); if(card){ card.remove(); card=null; }
    if(s.answer){ add("bot", s.answer); }
    else if(s.state==="blocked"){ add("sys","Blocked: "+(s.error||"not allowed")); }
    else if(s.state==="failed"){ add("sys","Failed: "+(s.error||"something went wrong")); }
    else { add("bot", "(no answer)"); }
    busy=false;
  };
  async function decide(allow){
    if(card){ card.querySelectorAll("button").forEach(b=>b.disabled=true); }
    await api("/api/approve",{task_id:sid, allow:allow});
    add("sys", allow? "You allowed it." : "You denied it.");
    const t2=document.createElement("div"); t2.className="typing"; t2.textContent="AERQEN kaam kar raha hai…"; log.appendChild(t2);
    setTimeout(()=>{ if(card){card.remove();card=null;} t2.remove(); poll(); }, 300);
  }
  setTimeout(poll, 700);
});
function escapeHtml(s){ return (s||"").replace(/[&<>]/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c])); }
</script>
</body>
</html>"""


class _Handler(BaseHTTPRequestHandler):
    service: AgentService = None  # set on the class before serving
    token: str = ""

    def log_message(self, *args):  # keep the console clean
        return

    # --- helpers ---------------------------------------------------------
    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, obj) -> None:
        self._send(code, json.dumps(obj).encode("utf-8"), "application/json")

    def _ok_token(self) -> bool:
        if not self.token:
            return True
        supplied = self.headers.get("X-AERQEN-Token", "")
        if not supplied:
            supplied = parse_qs(urlparse(self.path).query).get("t", [""])[0]
        return secrets.compare_digest(supplied, self.token)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {}

    # --- routes ----------------------------------------------------------
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
            return
        if not self._ok_token():
            self._json(403, {"error": "bad or missing token"})
            return
        if path == "/api/poll":
            sid = parse_qs(urlparse(self.path).query).get("task_id", [""])[0]
            self._json(200, self.service.poll(sid))
            return
        self._json(404, {"error": "not found"})

    def do_POST(self):
        # Always drain the request body first, even if we are about to refuse: replying
        # without reading the body aborts the connection on the client (WinError 10053).
        data = self._read_json()
        if not self._ok_token():
            self._json(403, {"error": "bad or missing token"})
            return
        path = urlparse(self.path).path
        if path == "/api/ask":
            message = str(data.get("message", "")).strip()
            if not message:
                self._json(400, {"error": "empty message"})
                return
            self._json(200, {"task_id": self.service.start(message)})
            return
        if path == "/api/approve":
            ok = self.service.approve(str(data.get("task_id", "")), bool(data.get("allow")))
            self._json(200, {"ok": ok})
            return
        self._json(404, {"error": "not found"})


def _lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def main() -> int:
    settings = load_settings()
    token = settings.web_token or secrets.token_urlsafe(6)

    def build(approver):
        return build_agent(approver=approver, audit=JsonlAuditLog(), settings=settings)

    _Handler.service = AgentService(build)
    _Handler.token = token

    httpd = ThreadingHTTPServer((settings.web_host, settings.web_port), _Handler)
    ip = _lan_ip()
    port = settings.web_port
    print("=" * 60)
    print("  AERQEN chat is running. Open one of these in a browser:")
    print(f"    This PC : http://localhost:{port}/?t={token}")
    print(f"    Phone   : http://{ip}:{port}/?t={token}   (same WiFi)")
    print("=" * 60)
    print("  Keep this window open. Press Ctrl+C to stop.")
    print("  (If your phone can't connect, allow Python through the Windows firewall.)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping AERQEN chat.")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
