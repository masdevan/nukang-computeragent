import pages.settings_page as settings_page


def test_wipe_all_data(tmp_path, monkeypatch):
    sessions_dir = tmp_path / "sessions"
    captures_dir = tmp_path / "captures"
    ocr_dir = tmp_path / "ocr"
    sessions_dir.mkdir()
    captures_dir.mkdir()
    ocr_dir.mkdir()
    (sessions_dir / "a.json").write_text("{}")
    (sessions_dir / "b.json").write_text("{}")
    (captures_dir / "x.png").write_bytes(b"png")
    (captures_dir / "y.png").write_bytes(b"png")
    (ocr_dir / "x.txt").write_text("ocr")

    monkeypatch.setattr(settings_page, "SESSIONS_DIR", sessions_dir)
    monkeypatch.setattr(settings_page, "CAPTURES_DIR", captures_dir)
    monkeypatch.setattr(settings_page, "OCR_DIR", ocr_dir)

    removed = settings_page.wipe_all_data()
    assert removed == 5
    assert list(sessions_dir.iterdir()) == []
    assert list(captures_dir.iterdir()) == []
    assert list(ocr_dir.iterdir()) == []


def test_wipe_all_data_empty_dirs(tmp_path, monkeypatch):
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setattr(settings_page, "SESSIONS_DIR", empty)
    monkeypatch.setattr(settings_page, "CAPTURES_DIR", empty)
    monkeypatch.setattr(settings_page, "OCR_DIR", empty)
    assert settings_page.wipe_all_data() == 0
