import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skills import drag


def test_drag_calls_mouse_sequence(monkeypatch):
    calls = []

    def fake_move(x, y):
        calls.append(("move", x, y))

    def fake_down(button):
        calls.append(("down", button))

    def fake_up(button):
        calls.append(("up", button))

    monkeypatch.setattr(drag, "move_to", fake_move)
    monkeypatch.setattr(drag, "mouse_down", fake_down)
    monkeypatch.setattr(drag, "mouse_up", fake_up)
    monkeypatch.setattr(drag.time, "sleep", lambda s: None)

    result = drag.drag(100, 100, 200, 300)

    assert result == "Dragged from (100,100) to (200,300)"
    assert calls[0] == ("move", 100, 100)
    assert calls[1] == ("down", "left")
    assert calls[-1] == ("up", "left")
    moves = [c for c in calls if c[0] == "move"]
    assert len(moves) == drag.DRAG_STEPS + 1
    assert moves[-1] == ("move", 200, 300)
