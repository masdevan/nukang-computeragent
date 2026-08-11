from app.services import prompt
from skills.chrome import _cdp, chrome_tabs


def test_chrome_visible_detects_window(monkeypatch):
    from skills.general import screenshot as shot

    monkeypatch.setattr(
        shot.ScreenshotCapture, "list_windows",
        lambda self: ["Google Chrome", "Visual Studio Code"],
    )
    assert _cdp.chrome_visible()
    monkeypatch.setattr(
        shot.ScreenshotCapture, "list_windows",
        lambda self: ["Visual Studio Code"],
    )
    assert not _cdp.chrome_visible()


def test_debug_alive_true(monkeypatch):
    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_open(url, timeout=1):
        return FakeResponse()

    monkeypatch.setattr(_cdp.urllib.request, "urlopen", fake_open)
    assert _cdp.debug_alive()


def test_debug_alive_false(monkeypatch):
    def fail(url, timeout=1):
        raise OSError("no chrome")

    monkeypatch.setattr(_cdp.urllib.request, "urlopen", fail)
    assert not _cdp.debug_alive()


def test_list_tabs_filters_and_marks_active(monkeypatch):
    monkeypatch.setattr(_cdp, "_http_get", lambda path: [
        {"type": "page", "id": "1", "title": "Alpha", "url": "https://a.com", "active": True},
        {"type": "page", "id": "2", "title": "Beta", "url": "https://b.com", "active": False},
        {"type": "other", "id": "3", "title": "Ext", "url": "https://ext", "active": False},
    ])
    tabs = _cdp.list_tabs()
    assert len(tabs) == 2
    assert tabs[0]["active"] is True
    assert tabs[1]["active"] is False


def test_activate_tab(monkeypatch):
    monkeypatch.setattr(_cdp, "_http_get", lambda path: None)
    assert _cdp.activate_tab("abc") == "Tab activated."


def test_evaluate_returns_value(monkeypatch):
    class FakeWs:
        def __init__(self, *a, **k):
            pass

        def send(self, payload):
            pass

        def recv(self):
            return '{"id": 1, "result": {"result": {"type": "string", "value": "Hello Page"}}}'

        def close(self):
            pass

    monkeypatch.setattr(_cdp, "list_tabs", lambda: [
        {"id": "1", "title": "A", "url": "https://a", "active": True,
         "webSocketDebuggerUrl": "ws://x"},
    ])
    monkeypatch.setattr(_cdp.websocket, "create_connection", FakeWs)
    assert _cdp.evaluate("document.body.innerText") == "Hello Page"


def test_evaluate_truncates_long_result(monkeypatch):
    class FakeWs:
        def __init__(self, *a, **k):
            pass

        def send(self, payload):
            pass

        def recv(self):
            value = "x" * (_cdp.MAX_RESULT_CHARS + 500)
            return f'{{"id": 1, "result": {{"result": {{"type": "string", "value": "{value}"}}}}}}'

        def close(self):
            pass

    monkeypatch.setattr(_cdp, "list_tabs", lambda: [
        {"id": "1", "title": "A", "url": "https://a", "active": True,
         "webSocketDebuggerUrl": "ws://x"},
    ])
    monkeypatch.setattr(_cdp.websocket, "create_connection", FakeWs)
    result = _cdp.evaluate("document.body.innerText")
    assert "truncated" in result
    assert len(result) <= _cdp.MAX_RESULT_CHARS + 100


def test_debug_status_off_never_restarts_chrome(monkeypatch):
    monkeypatch.setattr(_cdp, "debug_alive", lambda: False)
    ok, message = _cdp.debug_status()
    assert ok is False
    assert "chrome_enable_debugging" in message


def test_debug_status_on(monkeypatch):
    monkeypatch.setattr(_cdp, "debug_alive", lambda: True)
    ok, message = _cdp.debug_status()
    assert ok is True
    assert "connected" in message


def test_enable_debug_chrome_launches_with_flags(monkeypatch):
    launched = []
    monkeypatch.setattr(_cdp, "debug_alive", lambda: False)
    monkeypatch.setattr(_cdp.close_app, "close_app", lambda title: None)
    monkeypatch.setattr(_cdp.subprocess, "Popen", lambda cmd: launched.append(cmd))
    monkeypatch.setattr(_cdp.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(_cdp, "find_app_path", lambda name: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
    ok, message = _cdp.enable_debug_chrome()
    assert launched == [["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                         "--remote-debugging-port=9222", "--restore-last-session"]]
    assert ok is False
    assert "not responding" in message


def test_enable_debug_chrome_reuses_alive_connection(monkeypatch):
    monkeypatch.setattr(_cdp, "debug_alive", lambda: True)
    ok, message = _cdp.enable_debug_chrome()
    assert ok is True
    assert "connected" in message


def test_chrome_list_tabs_formats_output(monkeypatch):
    monkeypatch.setattr(_cdp, "debug_status", lambda: (True, "Chrome debugging connected."))
    monkeypatch.setattr(_cdp, "list_tabs", lambda: [
        {"title": "Alpha", "url": "https://a.com", "active": True},
        {"title": "Beta", "url": "https://b.com", "active": False},
    ])
    result = chrome_tabs.chrome_list_tabs({})
    assert "0: Alpha — https://a.com (active)" in result
    assert "1: Beta — https://b.com" in result


def test_chrome_switch_tab_by_index_and_text(monkeypatch):
    monkeypatch.setattr(_cdp, "debug_status", lambda: (True, "ok"))
    monkeypatch.setattr(_cdp, "list_tabs", lambda: [
        {"id": "1", "title": "Alpha", "url": "https://a.com", "active": True},
        {"id": "2", "title": "Beta", "url": "https://b.com", "active": False},
    ])
    monkeypatch.setattr(_cdp, "activate_tab", lambda tab_id: f"activated {tab_id}")
    assert chrome_tabs.chrome_switch_tab({"index": 1}) == "activated 2"
    assert chrome_tabs.chrome_switch_tab({"url": "b.com"}) == "activated 2"
    assert chrome_tabs.chrome_switch_tab({"title": "Alpha"}) == "activated 1"
    assert chrome_tabs.chrome_switch_tab({"index": 9}) == "Invalid tab index: 9"
    assert chrome_tabs.chrome_switch_tab({"title": "zzz"}) == "No tab matches: zzz"


def test_chrome_tools_block_lists_all_tools():
    block = prompt.chrome_tools_block()
    assert "Chrome is open" in block
    for tool in prompt.CHROME_TOOLS:
        assert tool["name"] in block


def test_tools_block_not_in_general_prompt():
    system = prompt.build_system_prompt("Indonesian")
    assert "chrome_list_tabs" not in system
