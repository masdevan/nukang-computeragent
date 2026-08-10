import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services import executors

corner_calls = []


def fake_corner():
    corner_calls.append(1)


executors.reposition_app_to_corner = fake_corner


def test_capture_screen_moves_app_first(monkeypatch):
    corner_calls.clear()
    monkeypatch.setattr(executors, "capture_region", lambda: (0, 0, 1920, 1080))
    monkeypatch.setattr(executors.screenshot.ScreenshotCapture, "capture_screen", lambda self, path=None, region=None: "fake.png")
    monkeypatch.setattr(executors.ocr, "write_ocr_sidecar", lambda path: "100 lines\nx")

    result = executors.capture_screen({})
    assert corner_calls == [1]
    assert "fake.png" in result


def test_scroll_moves_app_first(monkeypatch):
    corner_calls.clear()
    monkeypatch.setattr(executors, "current_position", lambda: (500, 500))
    monkeypatch.setattr(executors, "mouse_scroll", lambda amount, x, y: None)

    executors.scroll({"amount": -4})
    assert corner_calls == [1]
