import ctypes
import sys

WM_CLOSE = 0x0010


def close_app(title, protected_hwnd=None):
    if sys.platform != "win32":
        return "Closing apps is only supported on Windows."
    hwnd = find_window_hwnd(title)
    if hwnd is None:
        return f"Window not found: {title}"
    if protected_hwnd is not None and hwnd == protected_hwnd:
        return "Refused: cannot close the Nukang application itself."
    ctypes.windll.user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
    return f"Close requested for: {title}"


def find_window_hwnd(title):
    from skills.general.screenshot import ScreenshotCapture

    user32 = ctypes.windll.user32
    wanted = title.lower()
    for window_title in ScreenshotCapture().list_windows():
        if wanted in window_title.lower():
            return user32.FindWindowW(None, window_title)
    return None
