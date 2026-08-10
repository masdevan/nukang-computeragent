import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services import tools

corner_calls = []


def fake_corner():
    corner_calls.append(1)


tools.reposition_app_to_corner = fake_corner


def test_capture_screen_moves_app_first(monkeypatch):
    corner_calls.clear()
    monkeypatch.setattr(tools, "capture_region", lambda: (0, 0, 1920, 1080))
    monkeypatch.setattr(tools.screenshot.ScreenshotCapture, "capture_screen", lambda self, path=None, region=None: "fake.png")
    monkeypatch.setattr(tools.ocr, "write_ocr_sidecar", lambda path: "100 lines\nx")

    result = tools.capture_screen({})
    assert corner_calls == [1]
    assert "fake.png" in result


def test_scroll_moves_app_first(monkeypatch):
    corner_calls.clear()
    monkeypatch.setattr(tools, "current_position", lambda: (500, 500))
    monkeypatch.setattr(tools, "mouse_scroll", lambda amount, x, y: None)

    tools.scroll({"amount": -4})
    assert corner_calls == [1]
