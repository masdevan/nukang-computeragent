import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skills.general import _mouse


def test_smooth_steps_end_at_target():
    steps = _mouse.smooth_steps(100, 100, 500, 300)
    assert steps[-1] == (500, 300)
    assert steps[0] != (100, 100)


def test_smooth_steps_monotonic():
    steps = _mouse.smooth_steps(100, 100, 500, 100)
    xs = [x for x, y in steps]
    assert xs == sorted(xs)


def test_smooth_steps_ease_out():
    steps = _mouse.smooth_steps(100, 100, 500, 100)
    early = steps[1][0] - steps[0][0]
    late = steps[-1][0] - steps[-2][0]
    assert early > late


def test_smooth_steps_short_distance_min_duration():
    steps = _mouse.smooth_steps(100, 100, 110, 100)
    assert len(steps) >= 2


def test_move_to_smooth_uses_steps(monkeypatch):
    calls = []
    monkeypatch.setattr(_mouse, "current_position", lambda: (100, 100))
    monkeypatch.setattr(_mouse.ctypes.windll.user32, "SetCursorPos", lambda x, y: calls.append((x, y)))
    monkeypatch.setattr(_mouse.time, "sleep", lambda s: None)

    _mouse.move_to(500, 300, smooth=True)
    assert calls[-1] == (500, 300)
    assert len(calls) > 2


def test_move_to_instant_single_jump(monkeypatch):
    calls = []
    monkeypatch.setattr(_mouse.ctypes.windll.user32, "GetSystemMetrics", lambda index: 1920 if index == 0 else 1080)
    monkeypatch.setattr(_mouse.ctypes.windll.user32, "mouse_event", lambda *args: calls.append(args))

    _mouse.move_to(500, 300, smooth=False)
    assert len(calls) == 1
