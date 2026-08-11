import json
import time

from app.services import apps


def test_list_installed_apps_merges_and_dedups(monkeypatch):
    monkeypatch.setattr(apps, "_sources", lambda: [lambda: ["B", "A"], lambda: ["A", "C"]])
    assert apps.list_installed_apps() == ["A", "B", "C"]


def test_parse_desktop_name(tmp_path):
    good = tmp_path / "firefox.desktop"
    good.write_text("[Desktop Entry]\nName=Firefox\nExec=firefox\nNoDisplay=false\n", encoding="utf-8")
    hidden = tmp_path / "hidden.desktop"
    hidden.write_text("[Desktop Entry]\nName=Secret\nNoDisplay=true\n", encoding="utf-8")
    localized = tmp_path / "loc.desktop"
    localized.write_text("[Desktop Entry]\nName=Editor\nName[fr]=Editeur\n", encoding="utf-8")
    assert apps._parse_desktop_name(good) == "Firefox"
    assert apps._parse_desktop_name(hidden) is None
    assert apps._parse_desktop_name(localized) == "Editor"


def test_linux_desktop_apps_scans_roots(tmp_path, monkeypatch):
    (tmp_path / "a.desktop").write_text("[Desktop Entry]\nName=Alpha\n", encoding="utf-8")
    (tmp_path / "b.desktop").write_text("[Desktop Entry]\nName=Beta\n", encoding="utf-8")
    monkeypatch.setattr(apps, "LINUX_DESKTOP_ROOTS", [tmp_path])
    assert apps.linux_desktop_apps() == ["Alpha", "Beta"]


def test_bundle_name_falls_back_to_folder(tmp_path):
    bundle = tmp_path / "My App.app"
    bundle.mkdir()
    assert apps._bundle_name(bundle) == "My App"
    plist = bundle / "Contents" / "Info.plist"
    plist.parent.mkdir(parents=True)
    plist.write_bytes(b'<?xml version="1.0"?><plist><dict><key>CFBundleName</key><string>RealName</string></dict></plist>')
    assert apps._bundle_name(bundle) == "RealName"


def test_macos_apps_scans_roots(tmp_path, monkeypatch):
    (tmp_path / "Alpha.app").mkdir()
    (tmp_path / "Nested").mkdir()
    (tmp_path / "Nested" / "Beta.app").mkdir()
    monkeypatch.setattr(apps, "MACOS_APP_ROOTS", [tmp_path])
    assert apps.macos_apps() == ["Alpha", "Beta"]


def test_start_apps_parses_stdout(monkeypatch):
    class FakeResult:
        stdout = "Google Chrome\nDiscord\n\nPostman\n"

    monkeypatch.setattr(apps.subprocess, "run", lambda *a, **k: FakeResult())
    assert apps.start_apps() == ["Discord", "Google Chrome", "Postman"]


def test_start_apps_handles_failure(monkeypatch):
    def fail(*a, **k):
        raise OSError("no powershell")

    monkeypatch.setattr(apps.subprocess, "run", fail)
    assert apps.start_apps() == []


def test_cache_fresh_and_stale(tmp_path, monkeypatch):
    import os

    monkeypatch.setattr(apps, "CACHE_PATH", tmp_path / "apps.json")
    apps.CACHE_PATH.write_text(json.dumps(["Chrome"]), encoding="utf-8")
    scanned = []
    monkeypatch.setattr(apps, "list_installed_apps", lambda: scanned.append(1) or ["New"])
    assert apps.cached_installed_apps() == ["Chrome"]
    assert scanned == []
    old = time.time() - 999999
    os.utime(apps.CACHE_PATH, (old, old))
    assert apps.cached_installed_apps() == ["New"]
