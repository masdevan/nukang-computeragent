import ctypes
import sys

from skills.general.close_app import find_window_hwnd

SW_RESTORE = 9


def app_refocus(title, protected_hwnd=None):
    if sys.platform != "win32":
        return "Refocusing windows is only supported on Windows."
    hwnd = find_window_hwnd(title)
    if hwnd is None:
        return f"Window not found: {title}"
    if protected_hwnd is not None and hwnd == protected_hwnd:
        return "Refused: cannot refocus the Nukang application itself."
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.BringWindowToTop(hwnd)
    if user32.GetForegroundWindow() != hwnd:
        current_thread = kernel32.GetCurrentThreadId()
        window_thread = user32.GetWindowThreadProcessId(hwnd, None)
        user32.AttachThreadInput(current_thread, window_thread, True)
        user32.SetForegroundWindow(hwnd)
        user32.AttachThreadInput(current_thread, window_thread, False)
    return f"Refocused: {title}"


def main():
    args = [arg for arg in sys.argv[1:] if arg != "--noop"]
    noop = "--noop" in sys.argv
    if len(args) != 1:
        print("Usage: python skills/app_refocus.py <title> [--noop]")
        return
    title = args[0]
    print(f"Refocusing '{title}'...")
    if noop:
        print("Dry run.")
        return
    print(app_refocus(title))


if __name__ == "__main__":
    sys.exit(main())
