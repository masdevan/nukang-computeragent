import ctypes
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skills import expand_window, minimize_window, switch_app, switch_desktop


def test_expand_windows_maximizes(monkeypatch):
    calls = []
    monkeypatch.setattr(expand_window, "find_window_hwnd", lambda title: 4242)
    monkeypatch.setattr(ctypes.windll.user32, "ShowWindow", lambda hwnd, cmd: calls.append((hwnd, cmd)))

    result = expand_window.expand_windows("Notepad", None)
    assert result == "Expanded: Notepad"
    assert calls == [(4242, 3)]


def test_expand_protected_window(monkeypatch):
    monkeypatch.setattr(expand_window, "find_window_hwnd", lambda title: 777)
    result = expand_window.expand_windows("Nukang", 777)
    assert "Refused" in result


def test_expand_unknown_window(monkeypatch):
    monkeypatch.setattr(expand_window, "find_window_hwnd", lambda title: None)
    assert "Window not found" in expand_window.expand_windows("x", None)


def test_minimize_and_hide_commands(monkeypatch):
    calls = []
    monkeypatch.setattr(minimize_window, "find_window_hwnd", lambda title: 4242)
    monkeypatch.setattr(ctypes.windll.user32, "ShowWindow", lambda hwnd, cmd: calls.append((hwnd, cmd)))

    assert "Minimized" in minimize_window.show_window("Notepad", None, 6, "Minimized")
    assert calls == [(4242, 6)]
    assert "Hidden" in minimize_window.show_window("Notepad", None, 0, "Hidden")
    assert calls == [(4242, 6), (4242, 0)]


def test_switch_app_combos(monkeypatch):
    combos = []
    monkeypatch.setattr(
        switch_app.KeyboardController, "press_combo",
        lambda self, combo: combos.append(combo),
    )
    switch_app.switch_app("next")
    switch_app.switch_app("previous")
    assert combos == ["alt+tab", "alt+shift+tab"]


def test_desktop_combo_per_platform():
    assert switch_desktop.desktop_combo("next", "win32") == "win+ctrl+right"
    assert switch_desktop.desktop_combo("previous", "win32") == "win+ctrl+left"
    assert switch_desktop.desktop_combo("next", "darwin") == "ctrl+right"
    assert switch_desktop.desktop_combo("next", "linux") == "super+page_down"
    assert switch_desktop.desktop_combo("previous", "linux") == "super+page_up"


def test_switch_desktop_dispatch(monkeypatch):
    combos = []
    monkeypatch.setattr(
        switch_desktop.KeyboardController, "press_combo",
        lambda self, combo: combos.append(combo),
    )
    switch_desktop.switch_desktop("next")
    assert combos == [switch_desktop.desktop_combo("next", sys.platform)]


def test_tools_registry_sync():
    from app.services.prompt import TOOLS
    from app.services.executors import EXECUTORS

    names = {tool["name"] for tool in TOOLS}
    assert names == set(EXECUTORS)
    for expected in ("expand_window", "minimize_window", "hide_window", "switch_app", "switch_desktop"):
        assert expected in names
