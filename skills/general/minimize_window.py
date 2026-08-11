import shutil
import subprocess
import sys
import time

from skills.general.close_app import find_window_hwnd

SW_MINIMIZE = 6
SW_HIDE = 0


def minimize_window(title, protected_hwnd=None):
    if sys.platform == "win32":
        return show_window(title, protected_hwnd, SW_MINIMIZE, "Minimized")
    if sys.platform == "darwin":
        return mac_minimize(title)
    return linux_minimize(title)


def hide_window(title, protected_hwnd=None):
    if sys.platform == "win32":
        return show_window(title, protected_hwnd, SW_HIDE, "Hidden")
    if sys.platform == "darwin":
        return mac_hide(title)
    return linux_hide(title)


def show_window(title, protected_hwnd, command, action):
    import ctypes

    hwnd = find_window_hwnd(title)
    if hwnd is None:
        return f"Window not found: {title}"
    if protected_hwnd is not None and hwnd == protected_hwnd:
        return "Refused: cannot control the Nukang application itself."
    ctypes.windll.user32.ShowWindow(hwnd, command)
    return f"{action}: {title}"


def mac_minimize(title):
    return mac_script(
        f'set miniaturized of window 1 of (first process whose name contains "{title}") to true',
        "Minimized", title,
    )


def mac_hide(title):
    return mac_script(
        f'set visible of (first process whose name contains "{title}") to false',
        "Hidden", title,
    )


def mac_script(statement, action, title):
    if shutil.which("osascript") is None:
        return f"{action} needs osascript on macOS."
    result = subprocess.run(
        ["osascript", "-e", f'tell application "System Events" to {statement}'],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return f"Could not {action.lower()}: {title} ({result.stderr.strip()})"
    return f"{action}: {title}"


def linux_minimize(title):
    if shutil.which("xdotool") is None:
        return "Minimizing needs xdotool on Linux (install xdotool)."
    result = subprocess.run(["xdotool", "search", "--name", title, "windowminimize"], capture_output=True, text=True)
    if result.returncode != 0:
        return f"Could not minimize: {title}"
    return f"Minimized: {title}"


def linux_hide(title):
    if shutil.which("wmctrl") is None:
        return "Hiding needs wmctrl on Linux (install wmctrl)."
    result = subprocess.run(["wmctrl", "-r", title, "-b", "add,hidden"], capture_output=True, text=True)
    if result.returncode != 0:
        return f"Could not hide: {title}"
    return f"Hidden: {title}"


def main():
    args = [arg for arg in sys.argv[1:] if arg != "--noop"]
    noop = "--noop" in sys.argv
    if len(args) != 2 or args[0] not in ("minimize", "hide"):
        print("Usage: python skills/minimize_window.py <minimize|hide> <title> [--noop]")
        return
    action, title = args
    print(f"{action.capitalize()} '{title}' in 1s...")
    time.sleep(1)
    if noop:
        print("Dry run.")
        return
    if action == "minimize":
        print(minimize_window(title))
    else:
        print(hide_window(title))


if __name__ == "__main__":
    sys.exit(main())
