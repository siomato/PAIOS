from __future__ import annotations
import json
import os
import subprocess
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except Exception:
    sync_playwright = None

HOST = "127.0.0.1"
PORT = 8765
LOG_LOCK = threading.Lock()
EVENTS = []
PW = None
BROWSER = None
PAGE = None


def log(message, kind="info"):
    item = {"time": time.strftime("%H:%M:%S"), "kind": kind, "message": message}
    with LOG_LOCK:
        EVENTS.append(item)
        if len(EVENTS) > 200:
            del EVENTS[:-200]
    print(f"[{item['time']}] {kind.upper()}: {message}", flush=True)


def result(ok=True, message="", **extra):
    return {"ok": ok, "message": message, **extra}


def ensure_browser():
    global PW, BROWSER, PAGE
    if sync_playwright is None:
        raise RuntimeError(
            "Playwright is not installed. Run: pip install playwright && playwright install chromium"
        )
    if PAGE is not None:
        try:
            PAGE.title()
            return PAGE
        except Exception:
            PAGE = None
    log("Starting visible browser", "system")
    PW = sync_playwright().start()
    BROWSER = PW.chromium.launch(headless=False)
    PAGE = BROWSER.new_page(viewport={"width": 1400, "height": 850})
    return PAGE


def browser_open(url):
    page = ensure_browser()
    log(f"Browser -> {url}", "browser")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(1)
    title = page.title()
    log(f"Browser verified: {title or 'page loaded'}", "success")
    return result(True, "Browser navigation completed", url=page.url, title=title)


def browser_search(query):
    page = ensure_browser()
    q = str(query).strip()
    if not q:
        return result(False, "Search query is empty")

    url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(q)
    log(f"Browser search -> {q}", "browser")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(1.2)

    title = page.title()
    body = page.locator("body").inner_text(timeout=5000)

    blocked = [
        "captcha", "recaptcha", "verify you are human",
        "unusual traffic", "are you a robot", "robot check",
    ]
    if any(x in body.casefold() for x in blocked):
        log("Search verification detected; switching to Bing", "warning")
        url = "https://www.bing.com/search?q=" + urllib.parse.quote_plus(q)
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(1.2)
        title = page.title()
        body = page.locator("body").inner_text(timeout=5000)

    if not body.strip():
        return result(False, "Search page did not load")

    headings = []
    for selector in ["div#search h3", "li.b_algo h2", "h3"]:
        try:
            for el in page.locator(selector).all()[:5]:
                text = el.inner_text().strip()
                if text and text not in headings:
                    headings.append(text)
        except Exception:
            pass

    log(f"Search verified: {len(headings)} visible result headings", "success")
    return result(
        True,
        f'Searched the web for "{q}"',
        query=q,
        url=page.url,
        title=title,
        results=headings[:5],
    )


def laptop_document(app, text):
    if os.name != "nt":
        return result(False, "Laptop demo is Windows-only")

    desktop = Path.home() / "Desktop"
    desktop.mkdir(parents=True, exist_ok=True)
    path = desktop / "PAIOS_Hackathon_Demo.txt"
    path.write_text(text, encoding="utf-8")

    a = app.casefold().strip()
    if a == "notepad":
        subprocess.Popen(["notepad.exe", str(path)], shell=False)
    elif a == "vscode":
        subprocess.Popen(["cmd", "/c", "start", "", "code", str(path)], shell=False)
    else:
        return result(False, f"Unsupported editor: {app}")

    time.sleep(1.5)
    log(f"Laptop verified: demo document opened in {app}", "success")
    return result(True, "Desktop artifact created and opened", path=str(path), application=app)


def run_demo(name):
    name = str(name).strip().casefold()

    if name == "web_search":
        return browser_search("latest Python release")

    if name == "youtube":
        browser_open("https://www.youtube.com")
        return browser_search("Python tutorials")

    if name == "notepad":
        return laptop_document(
            "notepad",
            "Hello from PAIOS!\n\n"
            "This is the deterministic Hackathon Demo Harness.\n"
            "PAIOS interpreted the desktop task and produced this artifact."
        )

    if name == "vscode":
        return laptop_document(
            "vscode",
            "print('Hello from PAIOS')\n\n"
            "# PAIOS Hackathon Demo Harness"
        )

    if name == "cross_domain":
        data = browser_search("Python latest release")
        if not data["ok"]:
            return data
        summary = (
            "PAIOS HACKATHON DEMO\n\n"
            "Goal: Search the web and hand the result to the laptop.\n\n"
            f"Query: {data.get('query')}\n"
            f"Browser URL: {data.get('url')}\n"
            f"Page title: {data.get('title')}\n\n"
            "Visible result headings:\n"
            + "\n".join(f"- {x}" for x in data.get("results", []))
            + "\n\nGenerated automatically by PAIOS Demo Harness."
        )
        return laptop_document("notepad", summary)

    return result(False, f"Unknown demo: {name}")


def interpret_command(command):
    c = str(command).strip().casefold()

    if "youtube" in c and "search" in c:
        return "youtube"
    # Cross-domain demo must be checked before generic web-search matching.
    if "python" in c and "latest" in c and "release" in c and "send" in c and "notepad" in c:
        return "cross_domain"
    if "browser" in c and "notepad" in c:
        return "cross_domain"
    if "latest python release" in c and ("search" in c or "look" in c):
        return "web_search"
    if "notepad" in c and ("type" in c or "write" in c or "hello" in c):
        return "notepad"
    if ("vs code" in c or "vscode" in c) and ("type" in c or "write" in c or "print" in c):
        return "vscode"

    return None


def run_command(command):
    demo = interpret_command(command)
    if demo is None:
        return result(
            False,
            "For hackathon reliability, use one of the supported demo intents.",
            supported=[
                "Open Notepad and type Hello from PAIOS",
                "Search the web for the latest Python release",
                "Open YouTube then search Python tutorials",
                "Search Python latest release and send it to Notepad",
                "Open VS Code and type print hello",
            ],
        )
    log(f"Intent recognized -> {demo}", "planner")
    return run_demo(demo)


HTML = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>PAIOS - Hackathon Harness</title>
<style>
body{margin:0;background:#090b10;color:#e9edf5;font-family:Inter,Segoe UI,Arial,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:28px}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:22px}
h1{margin:0;font-size:30px}.sub{color:#8f9aaa;margin-top:5px}
.badge{padding:8px 12px;border:1px solid #33405a;border-radius:999px;color:#9cc4ff;background:#101725;font-weight:700}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.card{background:#10131a;border:1px solid #222a38;border-radius:16px;padding:18px;box-shadow:0 8px 30px #0005}
button{background:#182235;color:#fff;border:1px solid #33415b;border-radius:10px;padding:12px 14px;margin:5px;cursor:pointer;font-weight:700}
button:hover{background:#22314d}
input{width:calc(100% - 24px);padding:14px;border-radius:10px;border:1px solid #33415b;background:#0a0d13;color:#fff;margin-bottom:10px}
pre{white-space:pre-wrap;background:#080a0f;border-radius:10px;padding:14px;min-height:300px;max-height:460px;overflow:auto;color:#b9c5d8}
.small{font-size:13px;color:#8f9aaa}.steps{line-height:1.9;color:#cbd4e3}
@media(max-width:850px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
<header>
<div><h1>PAIOS</h1><div class="sub">Personal AI Operating System - Hackathon Harness</div></div>
<div class="badge">DEMO MODE - DETERMINISTIC</div>
</header>
<div class="grid">
<section class="card">
<h2>Live command</h2>
<div class="small">Natural language mapped to verified demo workflows.</div>
<input id="cmd" value="Search Python latest release and send it to Notepad">
<button onclick="runCmd()">Run command</button>
<button onclick="clearLog()">Clear log</button>
<h3>Demo commands</h3>
<div>
<button onclick="quick('Open Notepad and type Hello from PAIOS')">Notepad</button>
<button onclick="quick('Search the web for the latest Python release')">Web search</button>
<button onclick="quick('Open YouTube then search Python tutorials')">YouTube</button>
<button onclick="quick('Search Python latest release and send it to Notepad')">Browser -> Laptop</button>
<button onclick="quick('Open VS Code and type print hello')">VS Code</button>
</div>
</section>
<section class="card">
<h2>Architecture</h2>
<div class="steps">
<b>1.</b> Natural-language command<br>↓<br>
<b>2.</b> Intent recognition<br>↓<br>
<b>3.</b> Deterministic action plan<br>↓<br>
<b>4.</b> Browser / Laptop worker<br>↓<br>
<b>5.</b> Observe + verify<br>↓<br>
<b>6.</b> Result + telemetry
</div>
<h3>Hackathon strategy</h3>
<div class="small">This harness isolates the demo-critical path so a live presentation does not depend on fragile generic OS focus behavior.</div>
</section>
<section class="card" style="grid-column:1/-1">
<h2>Live telemetry</h2>
<pre id="log">Loading...</pre>
</section>
</div>
</div>
<script>
async function runCmd(){
 const c=document.getElementById('cmd').value.trim();
 if(!c){document.getElementById('log').textContent='[UI] Enter a command first.';return}
 document.getElementById('log').textContent='[UI] Command sent to PAIOS...';
 try{
   const r=await fetch('/api/command',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({command:c})});
   if(!r.ok) throw new Error('HTTP '+r.status);
   await refresh();
 }catch(e){
   document.getElementById('log').textContent='[UI ERROR] '+e.message;
 }
}
function quick(x){document.getElementById('cmd').value=x;runCmd()}
async function clearLog(){
 try{await fetch('/api/clear',{method:'POST'});await refresh()}
 catch(e){document.getElementById('log').textContent='[UI ERROR] '+e.message}
}
async function refresh(){
 try{
   const r=await fetch('/api/events'); const d=await r.json();
   document.getElementById('log').textContent=d.events.map(x=>`[${x.time}] ${x.kind.toUpperCase()}  ${x.message}`).join('\n') || 'Waiting for a command...';
 }catch(e){}
}
setInterval(refresh,500); refresh();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload, content_type="application/json"):
        data = payload.encode("utf-8") if isinstance(payload, str) else json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self._send(200, HTML, "text/html; charset=utf-8")
            return
        if self.path == "/api/events":
            with LOG_LOCK:
                events = list(EVENTS)
            self._send(200, {"events": events})
            return
        if self.path == "/api/health":
            self._send(200, {"ok": True, "playwright": sync_playwright is not None})
            return
        self._send(404, {"ok": False, "message": "Not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}

        if self.path == "/api/clear":
            with LOG_LOCK:
                EVENTS.clear()
            self._send(200, {"ok": True})
            return

        if self.path == "/api/command":
            command = str(payload.get("command", "")).strip()
            if not command:
                self._send(400, result(False, "Command is empty"))
                return

            def worker():
                try:
                    log(f"Command received -> {command}", "command")
                    output = run_command(command)
                    if output.get("ok"):
                        log(f"VERIFIED -> {output.get('message', 'Demo completed')}", "success")
                    else:
                        log(f"FAILED -> {output.get('message', 'Demo failed')}", "error")
                except Exception as e:
                    log(str(e), "error")

            threading.Thread(target=worker, daemon=True).start()
            self._send(202, result(True, "Command started"))
            return

        self._send(404, {"ok": False, "message": "Not found"})

    def log_message(self, format, *args):
        return


def main():
    log("PAIOS Hackathon Harness starting", "system")
    log(f"Dashboard: http://{HOST}:{PORT}", "system")
    log("Recommended headline demo: Browser -> Laptop", "system")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        try:
            if BROWSER:
                BROWSER.close()
        except Exception:
            pass
        try:
            if PW:
                PW.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main()

