import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skills.general import _click_try, find_and_click

CONTEXT_LINE = ("Who's using Chrome?", (100, 100, 200, 30), (200, 115), [])
TARGET_LINE = ("Devan Yudistira", (100, 300, 200, 30), (200, 315), [])
OTHER_LINE = ("Chrome", (100, 200, 80, 30), (140, 215), [])
EXPECT_LINE = ("Devan Yudistira - Google Chrome", (100, 400, 200, 30), (200, 415), [])


def build_harness(monkeypatch, state_machine):
    events = {"esc": 0, "closed": 0, "launched": 0}
    clicks = []
    state = {"name": "open"}

    def fake_capture():
        return state_machine(state["name"])

    def fake_click():
        clicks.append(1)
        if state["name"] == "open":
            state["name"] = "closed"
        elif state["name"] == "open2":
            state["name"] = "done"

    def fake_esc(self, combo):
        events["esc"] += 1

    def fake_close(name):
        events["closed"] += 1

    def fake_launch(name):
        events["launched"] += 1
        state["name"] = "open2"

    def fake_refocus(name):
        events["refocused"] = events.get("refocused", 0) + 1

    monkeypatch.setattr(_click_try, "capture_lines", fake_capture)
    monkeypatch.setattr(_click_try, "move_to", lambda x, y: None)
    monkeypatch.setattr(_click_try, "click", fake_click)
    monkeypatch.setattr(_click_try.time, "sleep", lambda s: None)
    monkeypatch.setattr(find_and_click.KeyboardController, "press_combo", fake_esc)
    monkeypatch.setattr("skills.general.close_app.close_app", fake_close)
    monkeypatch.setattr("skills.general.app_launcher.launch_app", fake_launch)
    monkeypatch.setattr("skills.general.app_refocus.app_refocus", fake_refocus)
    return events, clicks


def machine_open_then_closed(state):
    if state == "open" or state == "open2":
        return [CONTEXT_LINE, TARGET_LINE]
    if state == "done":
        return [EXPECT_LINE]
    return [OTHER_LINE]


def test_find_and_click_repositions_app_first(monkeypatch):
    calls = []
    monkeypatch.setattr(find_and_click, "reposition_corner", lambda: calls.append("corner"))
    monkeypatch.setattr(_click_try, "capture_lines", lambda: [TARGET_LINE])
    monkeypatch.setattr(_click_try, "move_to", lambda x, y: None)
    monkeypatch.setattr(_click_try, "click", lambda: None)
    monkeypatch.setattr(_click_try.time, "sleep", lambda s: None)

    result = find_and_click.find_and_click("Devan Yudistira")
    assert calls == ["corner"]
    assert "All attempts failed" in result


def test_context_lost_recovers_then_succeeds(monkeypatch):
    events, clicks = build_harness(monkeypatch, machine_open_then_closed)
    result = find_and_click.find_and_click(
        "Devan Yudistira",
        "Devan Yudistira - Google Chrome",
        "Who's using Chrome?",
        "chrome",
    )
    assert "success" in result
    assert events["esc"] >= 1
    assert events["refocused"] >= 1
    assert events["closed"] == 1
    assert events["launched"] == 1


def test_context_lost_without_app_name_fails_cleanly(monkeypatch):
    events, clicks = build_harness(monkeypatch, machine_open_then_closed)
    result = find_and_click.find_and_click(
        "Devan Yudistira",
        "Devan Yudistira - Google Chrome",
        "Who's using Chrome?",
        None,
    )
    assert "Context lost and could not be recovered" in result
    assert events["closed"] == 0
