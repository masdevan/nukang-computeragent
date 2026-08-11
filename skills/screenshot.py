import ctypes
import sys
from ctypes import wintypes
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CAPTURES_DIR = PROJECT_ROOT / "data" / "captures"
_current_session = ""


def set_session(session_id):
    global _current_session
    _current_session = session_id or ""


def current_session():
    return _current_session


def default_filename(prefix):
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{_current_session}_" if _current_session else ""
    return str(CAPTURES_DIR / f"{stem}{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")


class ScreenshotCapture:
    def capture_screen(self, path=None, region=None):
        import pyautogui

        if path is None:
            path = default_filename("screen")
        if region is None:
            image = pyautogui.screenshot()
        else:
            image = pyautogui.screenshot(region=region)
        image.save(path)
        print(f"Saved: {path} ({image.width}x{image.height})")
        return str(path)

    def capture_window(self, title, path=None):
        import pyautogui

        if sys.platform != "win32":
            print("Window capture is only supported on Windows.")
            return None
        if path is None:
            path = default_filename("window")
        hwnd = self.find_window(title)
        if hwnd is None:
            print(f"Window not found: {title}")
            return None
        rect = wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        left, top = rect.left, rect.top
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        if width <= 0 or height <= 0:
            print(f"Window has no visible area: {title}")
            return None
        image = pyautogui.screenshot(region=(left, top, width, height))
        image.save(path)
        print(f"Saved: {path} ({image.width}x{image.height})")
        return str(path)

    def list_windows(self):
        if sys.platform != "win32":
            return ["Window listing is only supported on Windows."]
        windows = []
        user32 = ctypes.windll.user32

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def enum_callback(hwnd, lparam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buffer, length + 1)
                    windows.append(buffer.value)
            return True

        user32.EnumWindows(enum_callback, 0)
        return windows

    def find_window(self, title):
        wanted = title.lower()
        for window_title in self.list_windows():
            if wanted in window_title.lower():
                return ctypes.windll.user32.FindWindowW(None, window_title)
        return None


def main():
    capture = ScreenshotCapture()
    print("Screenshot capture ready.")
    print("Commands: screen [file] | window <title> [file] | list | quit")
    while True:
        try:
            line = input("shot> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line == "quit":
            break
        if line == "list":
            for index, window_title in enumerate(capture.list_windows()):
                print(f"{index}: {window_title}")
            continue
        if line.startswith("screen"):
            parts = line.split()
            capture.capture_screen(parts[1] if len(parts) > 1 else None)
            continue
        if line.startswith("window"):
            parts = line.split(maxsplit=2)
            if len(parts) < 2:
                print("Usage: window <title> [file]")
                continue
            capture.capture_window(parts[1], parts[2] if len(parts) > 2 else None)
            continue
        print(f"Unknown command: {line}")


if __name__ == "__main__":
    sys.exit(main())
