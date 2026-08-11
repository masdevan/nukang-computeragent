import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skills.general import _click_try, find_and_click

FOUND_LINE = ("Devan Yudistira", (100, 100, 200, 30), (200, 115), [
    ("Devan", (100, 100, 80, 30), (140, 115)),
    ("Yudistira", (185, 100, 115, 30), (242, 115)),
])
OTHER_LINE = ("Chrome", (100, 200, 80, 30), (140, 215), [("Chrome", (100, 200, 80, 30), (140, 215))])
APP_LINE = ("Devan Yudistira", (500, 300, 200, 30), (600, 315), [
    ("Devan", (500, 300, 80, 30), (540, 315)),
    ("Yudistira", (585, 300, 115, 30), (642, 315)),
])


def test_click_candidates_dedup_and_clamp(monkeypatch):
    fake_pyautogui = types.ModuleType("pyautogui")
    fake_pyautogui.size = lambda: (1920, 1080)
    monkeypatch.setitem(sys.modules, "pyautogui", fake_pyautogui)
    points = _click_try.click_candidates((100, 100, 200, 30))
    assert (200, 115) in points
    assert (214, 115) in points
    assert (186, 115) in points
    assert len(points) == len(set(points))
    for x, y in points:
        assert 0 <= x < 1920 and 0 <= y < 1080


def test_click_candidates_small_box_few_points_no_corners(monkeypatch):
    fake_pyautogui = types.ModuleType("pyautogui")
    fake_pyautogui.size = lambda: (1920, 1080)
    monkeypatch.setitem(sys.modules, "pyautogui", fake_pyautogui)
    points = _click_try.click_candidates((100, 100, 40, 20))
    assert len(points) == 5
    assert (120, 110) in points
    assert (130, 110) in points
    assert (120, 115) in points


def test_click_candidates_large_box_has_corners(monkeypatch):
    fake_pyautogui = types.ModuleType("pyautogui")
    fake_pyautogui.size = lambda: (1920, 1080)
    monkeypatch.setitem(sys.modules, "pyautogui", fake_pyautogui)
    points = _click_try.click_candidates((100, 100, 200, 80))
    assert (110, 110) in points
    assert (290, 170) in points
    assert len(points) == 7


def test_attempt_loop_success_with_expect_text(monkeypatch):
    hits = []

    def fake_capture():
        if hits:
            return [("Devan Yudistira - Google Chrome", (0, 0, 100, 20), (50, 10), [])]
        return [OTHER_LINE]

    monkeypatch.setattr(_click_try, "capture_lines", fake_capture)
    monkeypatch.setattr(_click_try, "move_to", lambda x, y: None)
    monkeypatch.setattr(_click_try, "click", lambda: hits.append(1))
    monkeypatch.setattr(_click_try.time, "sleep", lambda s: None)

    result = _click_try.attempt_loop([(200, 115), (214, 115)], "devan yudistira - google chrome")
    assert "success" in result
    assert len(hits) == 1


def test_attempt_loop_all_fail(monkeypatch):
    monkeypatch.setattr(_click_try, "capture_lines", lambda: [OTHER_LINE])
    monkeypatch.setattr(_click_try, "move_to", lambda x, y: None)
    monkeypatch.setattr(_click_try, "click", lambda: None)
    monkeypatch.setattr(_click_try.time, "sleep", lambda s: None)

    result = _click_try.attempt_loop([(200, 115), (214, 115)], "tidak ada")
    assert "All attempts failed" in result
    assert "Attempt 1/2: clicked (200,115) -> no change" in result
    assert "Attempt 2/2: clicked (214,115) -> no change" in result


def test_attempt_loop_fingerprint_change_success(monkeypatch):
    states = iter([[OTHER_LINE], [OTHER_LINE, FOUND_LINE]])
    monkeypatch.setattr(_click_try, "capture_lines", lambda: next(states))
    monkeypatch.setattr(_click_try, "move_to", lambda x, y: None)
    monkeypatch.setattr(_click_try, "click", lambda: None)
    monkeypatch.setattr(_click_try.time, "sleep", lambda s: None)

    result = _click_try.attempt_loop([(200, 115)], None)
    assert "success" in result


def test_find_and_click_ignores_app_window(monkeypatch):
    monkeypatch.setattr(_click_try, "get_app_rect", lambda: (500, 300, 800, 600))
    monkeypatch.setattr(_click_try, "capture_lines", lambda: [APP_LINE])
    clicks = []
    monkeypatch.setattr(_click_try, "move_to", lambda x, y: None)
    monkeypatch.setattr(_click_try, "click", lambda: clicks.append(1))
    monkeypatch.setattr(_click_try.time, "sleep", lambda s: None)

    result = find_and_click.find_and_click("Devan Yudistira")
    assert "not found" in result
    assert clicks == []


def test_verify_success_via_window_title(monkeypatch):
    monkeypatch.setattr(_click_try, "capture_lines", lambda: [OTHER_LINE])
    monkeypatch.setattr(
        _click_try, "window_title_matches",
        lambda text: text.lower() == "devan yudistira - google chrome",
    )
    assert _click_try.verify_success("Devan Yudistira - Google Chrome", set())


def test_verify_success_via_ocr_first(monkeypatch):
    hit = ("Devan Yudistira - Google Chrome", (0, 0, 100, 20), (50, 10), [])
    monkeypatch.setattr(_click_try, "capture_lines", lambda: [hit])
    monkeypatch.setattr(_click_try, "window_title_matches", lambda text: False)
    assert _click_try.verify_success("Devan Yudistira - Google Chrome", set())


def test_try_click_reuses_candidates(monkeypatch):
    monkeypatch.setattr(_click_try, "capture_lines", lambda: [OTHER_LINE])
    monkeypatch.setattr(_click_try, "move_to", lambda x, y: None)
    monkeypatch.setattr(_click_try, "click", lambda: None)
    monkeypatch.setattr(_click_try.time, "sleep", lambda s: None)

    from skills.general import try_click

    result = try_click.try_click(500, 400)
    assert "All attempts failed" in result
