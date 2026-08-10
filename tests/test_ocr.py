from pathlib import Path

from skills import ocr


def fake_lines():
    return [
        ("Devan Yudistira", (880, 28, 150, 22), (955, 39), [
            ("Devan", (880, 28, 62, 22), (911, 39)),
            ("Yudistira", (946, 28, 84, 22), (988, 39)),
        ]),
    ]


def test_format_lines_structure():
    text = ocr.format_lines(fake_lines())
    assert '"Devan Yudistira" box(880, 28, 150, 22) center(955, 39)' in text
    assert '  "Devan" box(880, 28, 62, 22) center(911, 39)' in text
    assert '  "Yudistira" box(946, 28, 84, 22) center(988, 39)' in text


def test_format_lines_string_passthrough():
    assert ocr.format_lines("OCR unavailable") == "OCR unavailable"


def test_write_ocr_sidecar_full_and_capped(tmp_path, monkeypatch):
    monkeypatch.setattr(ocr, "ocr_file", lambda path: fake_lines())
    monkeypatch.setattr(ocr, "OCR_DIR", tmp_path)
    png = tmp_path / "screen.png"
    png.write_bytes(b"fake")
    feed = ocr.write_ocr_sidecar(str(png))
    sidecar = tmp_path / "screen.txt"
    full = sidecar.read_text(encoding="utf-8")
    assert full == feed
    assert "Devan" in full


def test_write_ocr_sidecar_truncates(monkeypatch):
    long_line = ("x" * 100, (0, 0, 100, 10), (50, 5), [])
    monkeypatch.setattr(ocr, "ocr_file", lambda path: [long_line] * 300)
    monkeypatch.setattr(ocr, "OCR_DIR", Path("unused"))
    feed = ocr.write_ocr_sidecar(Path("unused.png"))
    assert "truncated" in feed
    assert len(feed) <= ocr.MAX_MODEL_CHARS + 200
