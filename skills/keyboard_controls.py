import sys

COMMON_KEYS = [
    "enter", "esc", "tab", "space", "backspace", "delete",
    "up", "down", "left", "right",
    "ctrl", "alt", "shift", "win",
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
]


def parse_combo(combo):
    tokens = []
    for part in combo.strip().lower().split("+"):
        part = part.strip()
        if not part:
            continue
        if "*" in part:
            key, _, repeat = part.partition("*")
            repeat = int(repeat) if repeat.isdigit() else 1
        else:
            key, repeat = part, 1
        tokens.append((key.strip(), repeat))
    return tokens


class KeyboardController:
    def press_combo(self, combo):
        import pyautogui

        tokens = parse_combo(combo)
        for key, _ in tokens:
            self.check_key(key)
        if len(tokens) > 1 and all(repeat == 1 for _, repeat in tokens):
            pyautogui.hotkey(*[key for key, _ in tokens])
        else:
            for key, repeat in tokens:
                for _ in range(repeat):
                    pyautogui.keyDown(key)
                    pyautogui.keyUp(key)

    def press_key(self, key):
        import pyautogui

        self.check_key(key)
        pyautogui.keyDown(key)
        pyautogui.keyUp(key)

    def type_text(self, text):
        import pyautogui

        pyautogui.typewrite(text)

    def check_key(self, key):
        import pyautogui

        if key not in pyautogui.KEYBOARD_KEYS:
            print(f"Unknown key: {key}")


def main():
    controller = KeyboardController()
    print("Keyboard controls ready.")
    print("Usage: <combo>  |  type <text>  |  help  |  quit")
    print("Example: ctrl+shift+s, alt+tab, right*5, type halo")
    while True:
        try:
            line = input("combo> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line == "quit":
            break
        if line == "help":
            print("Common keys:", ", ".join(COMMON_KEYS))
            print("Modifiers: ctrl, alt, shift, win")
            print("Repeat with *N, e.g. left*3")
            continue
        if line.startswith("type "):
            controller.type_text(line[5:])
            continue
        controller.press_combo(line)


if __name__ == "__main__":
    sys.exit(main())
