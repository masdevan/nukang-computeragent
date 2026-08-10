import ctypes
import sys
from ctypes import wintypes

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_XDOWN = 0x0080
MOUSEEVENTF_XUP = 0x0100
XBUTTON1 = 0x0001
XBUTTON2 = 0x0002

BUTTONS = ["left", "right", "middle"]


class MouseController:
    def move_to(self, x, y):
        import pyautogui

        pyautogui.moveTo(x, y)

    def move_by(self, dx, dy):
        import pyautogui

        pyautogui.moveRel(dx, dy)

    def click(self, button="left"):
        import pyautogui

        if button not in BUTTONS:
            print(f"Unknown button: {button}")
            return
        pyautogui.click(button=button)

    def double_click(self):
        import pyautogui

        pyautogui.doubleClick()

    def scroll(self, amount):
        import pyautogui

        pyautogui.scroll(amount)

    def back(self):
        self.send_xbutton(XBUTTON1)

    def forward(self):
        self.send_xbutton(XBUTTON2)

    def position(self):
        import pyautogui

        return pyautogui.position()

    def send_xbutton(self, button):
        ctypes.windll.user32.SendInput(1, self.xbutton_input(button, MOUSEEVENTF_XDOWN), 32)
        ctypes.windll.user32.SendInput(1, self.xbutton_input(button, MOUSEEVENTF_XUP), 32)

    def xbutton_input(self, button, flags):
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

        mouse_input = MouseInput(0, 0, button, flags, 0, None)
        wrapper = Input(0, InputUnion(mi=mouse_input))
        return wrapper


def parse_move(text):
    text = text.strip()
    if text.startswith("+") or text.startswith("-"):
        parts = text.split()
        if len(parts) != 2:
            return None
        return ("relative", int(parts[0]), int(parts[1]))
    parts = text.split()
    if len(parts) != 2:
        return None
    return ("absolute", int(parts[0]), int(parts[1]))


def main():
    controller = MouseController()
    print("Mouse controls ready.")
    print("Commands: move <x> <y> | move +<dx> <dy> | click [left|right|middle] | double")
    print("          scroll <amount> | back | forward | position | help | quit")
    while True:
        try:
            line = input("mouse> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        command, _, rest = line.partition(" ")
        if command == "quit":
            break
        if command == "help":
            print("Buttons: left, right, middle")
            print("Scroll: positive up, negative down")
            continue
        if command == "move":
            parsed = parse_move(rest)
            if parsed is None:
                print("Usage: move <x> <y> or move +<dx> <dy>")
                continue
            kind, first, second = parsed
            if kind == "absolute":
                controller.move_to(first, second)
            else:
                controller.move_by(first, second)
            continue
        if command == "click":
            controller.click(rest.strip() or "left")
            continue
        if command == "double":
            controller.double_click()
            continue
        if command == "scroll":
            try:
                controller.scroll(int(rest))
            except ValueError:
                print("Usage: scroll <amount>")
            continue
        if command == "back":
            controller.back()
            continue
        if command == "forward":
            controller.forward()
            continue
        if command == "position":
            print(controller.position())
            continue
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    sys.exit(main())
