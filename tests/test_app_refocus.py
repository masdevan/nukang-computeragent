import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skills.general import app_refocus


def fake_user32(monkeypatch, calls, foreground_hwnd):
    def show_window(hwnd, cmd):
        calls.append(("show", hwnd, cmd))

    def bring_top(hwnd):
        calls.append(("bring", hwnd))

    def get_foreground():
        return foreground_hwnd

    def attach(current, target, attach):
        calls.append(("attach", current, target, attach))

    def set_foreground(hwnd):
        calls.append(("foreground", hwnd))

    monkeypatch.setattr(app_refocus.ctypes.windll.user32, "ShowWindow", show_window)
    monkeypatch.setattr(app_refocus.ctypes.windll.user32, "BringWindowToTop", bring_top)
    monkeypatch.setattr(app_refocus.ctypes.windll.user32, "GetForegroundWindow", get_foreground)
    monkeypatch.setattr(app_refocus.ctypes.windll.user32, "AttachThreadInput", attach)
    monkeypatch.setattr(app_refocus.ctypes.windll.user32, "SetForegroundWindow", set_foreground)
    monkeypatch.setattr(app_refocus.ctypes.windll.kernel32, "GetCurrentThreadId", lambda: 111)


def test_refocus_not_foreground_uses_attach_trick(monkeypatch):
    calls = []
    monkeypatch.setattr(app_refocus, "find_window_hwnd", lambda title: 4242)
    fake_user32(monkeypatch, calls, foreground_hwnd=9999)

    result = app_refocus.app_refocus("Notepad")
    assert result == "Refocused: Notepad"
    assert ("show", 4242, 9) in calls
    assert ("bring", 4242) in calls
    assert ("attach", 111, 0, True) in calls
    assert ("foreground", 4242) in calls
    assert ("attach", 111, 0, False) in calls


def test_refocus_already_foreground_skips_attach(monkeypatch):
    calls = []
    monkeypatch.setattr(app_refocus, "find_window_hwnd", lambda title: 4242)
    fake_user32(monkeypatch, calls, foreground_hwnd=4242)

    app_refocus.app_refocus("Notepad")
    assert not any(call[0] == "attach" for call in calls)


def test_refocus_unknown_window(monkeypatch):
    monkeypatch.setattr(app_refocus, "find_window_hwnd", lambda title: None)
    assert app_refocus.app_refocus("tidak-ada") == "Window not found: tidak-ada"


def test_refocus_protected_window(monkeypatch):
    monkeypatch.setattr(app_refocus, "find_window_hwnd", lambda title: 777)
    result = app_refocus.app_refocus("Nukang Computer Agent", protected_hwnd=777)
    assert "Refused" in result
