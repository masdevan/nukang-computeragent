from app.services import executors
from skills.general import screenshot
from skills.general import ocr as ocr_module


def test_default_filename_has_session_prefix():
    screenshot.set_session("abc123")
    name = screenshot.default_filename("screen")
    assert "abc123_screen_" in name
    screenshot.set_session("")


def test_default_filename_without_session_keeps_plain_name():
    screenshot.set_session("")
    name = screenshot.default_filename("screen")
    assert name.count("_") == 2
    assert "screen_" in name


def test_session_ocr_texts_orders_and_limits(tmp_path, monkeypatch):
    monkeypatch.setattr(ocr_module, "OCR_DIR", tmp_path)
    (tmp_path / "abc123_screen_1.txt").write_text("first", encoding="utf-8")
    (tmp_path / "abc123_screen_2.txt").write_text("second", encoding="utf-8")
    (tmp_path / "abc123_screen_3.txt").write_text("third", encoding="utf-8")

    full = ocr_module.session_ocr_texts("abc123")
    assert full.index("first") < full.index("second") < full.index("third")

    limited = ocr_module.session_ocr_texts("abc123", 2)
    assert "first" not in limited
    assert "second" in limited and "third" in limited


def test_session_ocr_texts_empty_and_no_session(tmp_path, monkeypatch):
    monkeypatch.setattr(ocr_module, "OCR_DIR", tmp_path)
    assert ocr_module.session_ocr_texts("abc123") == "No observations yet in this session."
    assert ocr_module.session_ocr_texts("") == "No session context."


def test_recall_observations_uses_current_session_and_limit(monkeypatch):
    calls = []
    monkeypatch.setattr(executors.ocr, "session_ocr_texts", lambda sid, limit: calls.append((sid, limit)) or "ok")
    screenshot.set_session("xyz")
    executors.recall_observations({"limit": 3})
    assert calls == [("xyz", 3)]
    screenshot.set_session("")
