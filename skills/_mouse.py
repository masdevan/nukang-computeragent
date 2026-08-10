import ctypes
import sys
import time
from ctypes import wintypes

MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800
WHEEL_DELTA = 120

BUTTON_FLAGS = {
    "left": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
    "right": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
}


def current_position():
    if sys.platform == "win32":
        point = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        return point.x, point.y
    import pyautogui

    pos = pyautogui.position()
    return pos.x, pos.y


def move_to(x, y, smooth=True):
    if smooth:
        smooth_move_to(x, y)
    else:
        instant_move_to(x, y)


def instant_move_to(x, y):
    if sys.platform == "win32":
        user32 = ctypes.windll.user32
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        absolute_x = int(x * 65535 / max(width - 1, 1))
        absolute_y = int(y * 65535 / max(height - 1, 1))
        user32.mouse_event(MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE, absolute_x, absolute_y, 0, 0)
    else:
        import pyautogui

        pyautogui.moveTo(x, y)


def smooth_move_to(x, y):
    if sys.platform == "win32":
        start_x, start_y = current_position()
        points = smooth_steps(start_x, start_y, x, y)
        user32 = ctypes.windll.user32
        for point_x, point_y in points:
            user32.SetCursorPos(point_x, point_y)
            time.sleep(0.012)
    else:
        import pyautogui

        pyautogui.moveTo(x, y, duration=0.25, tween=pyautogui.easeOutQuad)


def smooth_steps(start_x, start_y, target_x, target_y):
    distance = abs(target_x - start_x) + abs(target_y - start_y)
    duration_ms = max(90, min(350, distance * 0.6))
    step_count = max(2, int(duration_ms / 12))
    steps = []
    for step in range(1, step_count + 1):
        progress = step / step_count
        eased = 1 - (1 - progress) ** 3
        steps.append((
            round(start_x + (target_x - start_x) * eased),
            round(start_y + (target_y - start_y) * eased),
        ))
    return steps


def click(button, x=None, y=None, clicks=1, interval=0.05):
    if x is None or y is None:
        x, y = current_position()
    move_to(x, y)
    for _ in range(clicks):
        if sys.platform == "win32":
            user32 = ctypes.windll.user32
            down, up = BUTTON_FLAGS[button]
            user32.mouse_event(down, 0, 0, 0, 0)
            user32.mouse_event(up, 0, 0, 0, 0)
        else:
            import pyautogui

            pyautogui.click(x, y, button=button)
        time.sleep(interval)


def hold(button, x=None, y=None, seconds=1):
    if x is None or y is None:
        x, y = current_position()
    move_to(x, y)
    if sys.platform == "win32":
        user32 = ctypes.windll.user32
        down, up = BUTTON_FLAGS[button]
        user32.mouse_event(down, 0, 0, 0, 0)
        time.sleep(seconds)
        user32.mouse_event(up, 0, 0, 0, 0)
    else:
        import pyautogui

        pyautogui.mouseDown(x, y, button=button)
        time.sleep(seconds)
        pyautogui.mouseUp(x, y, button=button)


def mouse_down(button):
    if sys.platform == "win32":
        user32 = ctypes.windll.user32
        down, _ = BUTTON_FLAGS[button]
        user32.mouse_event(down, 0, 0, 0, 0)
    else:
        import pyautogui

        pyautogui.mouseDown(button=button)


def mouse_up(button):
    if sys.platform == "win32":
        user32 = ctypes.windll.user32
        _, up = BUTTON_FLAGS[button]
        user32.mouse_event(up, 0, 0, 0, 0)
    else:
        import pyautogui

        pyautogui.mouseUp(button=button)


def scroll(amount, x=None, y=None):
    original = None
    if x is not None and y is not None:
        original = current_position()
        move_to(x, y)
    if sys.platform == "win32":
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, amount * WHEEL_DELTA, 0)
    else:
        import pyautogui

        pyautogui.scroll(amount * WHEEL_DELTA)
    if original is not None:
        move_to(*original)


def xbutton(button):
    if sys.platform == "win32":
        send_xbutton_windows(button)
    elif sys.platform == "linux":
        xbutton_linux(button)
    else:
        xbutton_macos(button)


def send_xbutton_windows(button):
    user32 = ctypes.windll.user32
    data = 0x0001 if button == "back" else 0x0002
    for flags in (0x0080, 0x0100):
        user32.SendInput(1, xbutton_input(data, flags), 32)


def xbutton_input(data, flags):
    class MouseInput(ctypes.Structure):
        _fields_ = [
            ("dx", wintypes.LONG),
            ("dy", wintypes.LONG),
            ("mouseData", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        ]

    class InputUnion(ctypes.Union):
        _fields_ = [("mi", MouseInput)]

    class Input(ctypes.Structure):
        _fields_ = [("type", wintypes.DWORD), ("union", InputUnion)]

    mouse_input = MouseInput(0, 0, data, flags, 0, None)
    return Input(0, InputUnion(mi=mouse_input))


def xbutton_linux(button):
    import shutil
    import subprocess

    if shutil.which("xdotool") is None:
        print("Back/forward needs xdotool on Linux (install xdotool).")
        return
    subprocess.Popen(["xdotool", "click", "8" if button == "back" else "9"])


def xbutton_macos(button):
    try:
        from Quartz import (
            CGEventCreate, CGEventCreateMouseEvent, CGEventPost,
            kCGHIDEventTap, kCGEventOtherMouseDown, kCGEventOtherMouseUp,
        )
    except ImportError:
        print("Back/forward needs pyobjc on macOS (pip install pyobjc-framework-Quartz).")
        return
    location = CGEventCreate(None).location
    button_number = 3 if button == "back" else 4
    for event_type in (kCGEventOtherMouseDown, kCGEventOtherMouseUp):
        event = CGEventCreateMouseEvent(None, event_type, location, button_number)
        CGEventPost(kCGHIDEventTap, event)
