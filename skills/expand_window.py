import shutil
import subprocess
import sys
import time

from skills.close_app import find_window_hwnd

SW_MAXIMIZE = 3


def expand_window(title, protected_hwnd=None):
    if sys.platform == "win32":
        return expand_windows(title, protected_hwnd)
    if sys.platform == "darwin":
        return expand_macos(title)
    return expand_linux(title)


def expand_windows(title, protected_hwnd):
    import ctypes

    hwnd = find_window_hwnd(title)
    if hwnd is None:
        return f"Window not found: {title}"
    if protected_hwnd is not None and hwnd == protected_hwnd:
        return "Refused: cannot expand the Nukang application itself."
    ctypes.windll.user32.ShowWindow(hwnd, SW_MAXIMIZE)
    return f"Expanded: {title}"


def expand_macos(title):
    if shutil.which("osascript") is None:
        return "Expanding windows needs osascript on macOS."
    script = (
        'tell application "System Events" '
        f'to click button 1 of window 1 of (first process whose name contains "{title}")'
    )
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        return f"Could not expand: {title} ({result.stderr.strip()})"
    return f"Expanded: {title}"


def expand_linux(title):
    if shutil.which("wmctrl") is None:
        return "Expanding windows needs wmctrl on Linux (install wmctrl)."
    result = subprocess.run(
        ["wmctrl", "-r", title, "-b", "add,maximized_vert,maximized_horz"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return f"Could not expand: {title} ({result.stderr.strip()})"
    return f"Expanded: {title}"


def main():
    args = [arg for arg in sys.argv[1:] if arg != "--noop"]
    noop = "--noop" in sys.argv
    if len(args) != 1:
        print("Usage: python skills/expand_window.py <title> [--noop]")
        return
    title = args[0]
    print(f"Expanding '{title}' in 1s...")
    time.sleep(1)
    if noop:
        print("Dry run.")
        return
    print(expand_window(title))


if __name__ == "__main__":
    sys.exit(main())
