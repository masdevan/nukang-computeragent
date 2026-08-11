import json
import subprocess
import time
import urllib.request

import websocket

from skills.general import close_app
from skills.general.app_launcher import find_app_path

CDP_HTTP = "http://127.0.0.1:9222"
MAX_RESULT_CHARS = 8000
_launch_lock = False


def chrome_visible():
    from skills.general.screenshot import ScreenshotCapture

    return any("google chrome" in title.lower() for title in ScreenshotCapture().list_windows())


def debug_alive():
    try:
        with urllib.request.urlopen(f"{CDP_HTTP}/json/version", timeout=1) as response:
            return response.status == 200
    except (OSError, urllib.error.URLError):
        return False


def debug_status():
    if debug_alive():
        return True, "Chrome debugging connected."
    return False, (
        "Chrome remote debugging is not active. Use keyboard/mouse tools instead "
        "(chrome_search, capture_screen with OCR, find_and_click). To read page content "
        "or list tabs, call chrome_enable_debugging once — it restarts Chrome with remote "
        "debugging and restores your tabs."
    )


def enable_debug_chrome():
    global _launch_lock
    if debug_alive():
        return True, "Chrome debugging already connected."
    if _launch_lock:
        return False, "Chrome is restarting with debugging — retry in a moment."
    _launch_lock = True
    try:
        close_app.close_app("Google Chrome")
        time.sleep(1)
        path = find_app_path("chrome")
        if path is None:
            return False, "Chrome executable not found."
        subprocess.Popen([path, "--remote-debugging-port=9222", "--restore-last-session"])
        for _ in range(20):
            if debug_alive():
                return True, "Chrome restarted with remote debugging on port 9222; tabs restored."
            time.sleep(0.5)
        return False, "Chrome relaunched but debugging port is not responding yet."
    finally:
        _launch_lock = False


def _http_get(path):
    with urllib.request.urlopen(f"{CDP_HTTP}{path}", timeout=3) as response:
        return json.loads(response.read().decode("utf-8"))


def list_tabs():
    targets = _http_get("/json")
    tabs = []
    for target in targets:
        if target.get("type") != "page":
            continue
        tabs.append({
            "id": target.get("id"),
            "title": target.get("title") or "",
            "url": target.get("url") or "",
            "active": bool(target.get("active")),
        })
    return tabs


def activate_tab(tab_id):
    _http_get(f"/json/activate/{tab_id}")
    return "Tab activated."


def close_tab(tab_id):
    _http_get(f"/json/close/{tab_id}")
    return "Tab closed."


def evaluate(expression):
    tabs = list_tabs()
    active = next((tab for tab in tabs if tab.get("active")), tabs[0] if tabs else None)
    ws_url = active.get("webSocketDebuggerUrl") if active else None
    if ws_url is None:
        return "No active page tab to evaluate in."
    ws = websocket.create_connection(ws_url, timeout=10)
    try:
        ws.send(json.dumps({
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {"expression": expression, "returnByValue": True},
        }))
        while True:
            message = json.loads(ws.recv())
            if message.get("id") != 1:
                continue
            result = message.get("result", {}).get("result", {})
            if "exceptionDetails" in message.get("result", {}):
                return f"JS error: {message['result']['exceptionDetails'].get('text', 'unknown')}"
            value = result.get("value")
            text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
            if text is None:
                return "(no value)"
            if len(text) > MAX_RESULT_CHARS:
                text = text[:MAX_RESULT_CHARS] + f"\n...[truncated {len(text) - MAX_RESULT_CHARS} chars]"
            return text
    finally:
        ws.close()
