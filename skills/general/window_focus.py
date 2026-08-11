import sys

from skills.general.screenshot import ScreenshotCapture


def focus_window(title):
    if sys.platform != "win32":
        return "Focusing windows is only supported on Windows."
    import ctypes

    user32 = ctypes.windll.user32
    hwnd = None
    for window_title in ScreenshotCapture().list_windows():
        if title.lower() in window_title.lower():
            hwnd = user32.FindWindowW(None, window_title)
            break
    if hwnd is None:
        return f"Window not found: {title}"
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    return f"Focused: {title}"
