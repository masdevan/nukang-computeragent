from skills.general import close_app


def test_refuses_protected_window(monkeypatch):
    monkeypatch.setattr(close_app, "find_window_hwnd", lambda title: 4242)
    result = close_app.close_app("Nukang Computer Agent", protected_hwnd=4242)
    assert "Refused" in result
    assert "itself" in result


def test_close_unknown_window(monkeypatch):
    monkeypatch.setattr(close_app, "find_window_hwnd", lambda title: None)
    result = close_app.close_app("tidak-ada", protected_hwnd=4242)
    assert "Window not found" in result


def test_close_without_protection(monkeypatch):
    calls = []

    monkeypatch.setattr(close_app, "find_window_hwnd", lambda title: 1234)
    monkeypatch.setattr(close_app.ctypes.windll.user32, "PostMessageW", lambda hwnd, msg, w, l: calls.append(hwnd))
    result = close_app.close_app("Notepad")
    assert result == "Close requested for: Notepad"
    assert calls == [1234]
