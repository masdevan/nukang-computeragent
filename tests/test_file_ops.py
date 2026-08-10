import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skills import file_ops


def test_read_file_expands_env_vars(tmp_path, monkeypatch):
    target = tmp_path / "data.txt"
    target.write_text("isi file", encoding="utf-8")
    monkeypatch.setenv("NUKANG_TEST_DIR", str(tmp_path))

    result = file_ops.read_file("%NUKANG_TEST_DIR%/data.txt")
    assert result == "isi file"


def test_read_file_expands_home(tmp_path, monkeypatch):
    target = tmp_path / "home.txt"
    target.write_text("home", encoding="utf-8")
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path))

    assert file_ops.read_file("~/home.txt") == "home"
    assert file_ops.read_file("%USERPROFILE%/home.txt") == "home"
