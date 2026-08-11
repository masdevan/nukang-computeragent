import json
import os
import plistlib
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CACHE_PATH = PROJECT_ROOT / "data" / "apps.json"
CACHE_TTL_SECONDS = 24 * 3600

LINUX_DESKTOP_ROOTS = [
    Path.home() / ".local" / "share" / "applications",
    Path("/usr/local/share/applications"),
    Path("/usr/share/applications"),
    Path.home() / ".local" / "share" / "flatpak" / "exports" / "share" / "applications",
    Path("/var/lib/flatpak/exports/share/applications"),
    Path("/var/lib/snapd/desktop/applications"),
]

MACOS_APP_ROOTS = [
    Path("/Applications"),
    Path.home() / "Applications",
    Path("/System/Applications"),
]

UNINSTALL_ROOTS = [
    (r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", False),
    (r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall", False),
    (r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", True),
]

APP_PATHS_ROOT = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"


def list_installed_apps():
    names = set()
    for source in _sources():
        names.update(source())
    return sorted(name for name in names if name)


def _sources():
    if sys.platform == "win32":
        return [registry_apps, app_paths, start_apps]
    if sys.platform == "darwin":
        return [macos_apps]
    return [linux_desktop_apps]


def registry_apps():
    import winreg

    names = set()
    for path, current_user in UNINSTALL_ROOTS:
        hive = winreg.HKEY_CURRENT_USER if current_user else winreg.HKEY_LOCAL_MACHINE
        try:
            with winreg.OpenKey(hive, path) as key:
                for index in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        with winreg.OpenKey(key, winreg.EnumKey(key, index)) as app:
                            try:
                                if winreg.QueryValueEx(app, "SystemComponent")[0]:
                                    continue
                            except OSError:
                                pass
                            try:
                                winreg.QueryValueEx(app, "ParentKeyName")
                                continue
                            except OSError:
                                pass
                            try:
                                display_name = winreg.QueryValueEx(app, "DisplayName")[0]
                            except OSError:
                                continue
                            if display_name:
                                names.add(display_name.strip())
                    except OSError:
                        continue
        except OSError:
            continue
    return sorted(names)


def app_paths():
    import winreg

    tokens = set()
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(hive, APP_PATHS_ROOT) as key:
                for index in range(winreg.QueryInfoKey(key)[0]):
                    tokens.add(winreg.EnumKey(key, index))
        except OSError:
            continue
    return sorted(tokens)


def start_apps():
    try:
        result = subprocess.run(
            [
                "powershell", "-NoProfile", "-Command",
                "Get-StartApps | Where-Object { $_.Name } | Select-Object -ExpandProperty Name",
            ],
            capture_output=True, text=True, timeout=15,
        )
        return sorted(name.strip() for name in result.stdout.splitlines() if name.strip())
    except (OSError, subprocess.SubprocessError):
        return []


def linux_desktop_apps():
    names = set()
    for root in LINUX_DESKTOP_ROOTS:
        if not root.is_dir():
            continue
        for entry in root.glob("*.desktop"):
            name = _parse_desktop_name(entry)
            if name:
                names.add(name)
    return sorted(names)


def _parse_desktop_name(path):
    name = None
    no_display = False
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if stripped.startswith("Name=") and not stripped.startswith("Name["):
                name = stripped[5:].strip()
            elif stripped == "NoDisplay=true":
                no_display = True
    except OSError:
        return None
    if no_display or not name:
        return None
    return name


def macos_apps():
    names = set()
    for root in MACOS_APP_ROOTS:
        if not root.is_dir():
            continue
        for bundle in list(root.glob("*.app")) + list(root.glob("*/*.app")):
            names.add(_bundle_name(bundle))
    return sorted(name for name in names if name)


def _bundle_name(bundle):
    plist_path = bundle / "Contents" / "Info.plist"
    if plist_path.exists():
        try:
            with plist_path.open("rb") as handle:
                info = plistlib.load(handle)
            return info.get("CFBundleDisplayName") or info.get("CFBundleName") or bundle.stem
        except (OSError, ValueError):
            pass
    return bundle.stem


def cached_installed_apps():
    if CACHE_PATH.exists() and time.time() - CACHE_PATH.stat().st_mtime < CACHE_TTL_SECONDS:
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
    return refresh_installed_apps()


def refresh_installed_apps():
    apps = list_installed_apps()
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(apps, indent=2), encoding="utf-8")
    return apps
