import sys
import time

from skills.general.keyboard_controls import KeyboardController


def desktop_combo(direction, platform):
    key = "right" if direction == "next" else "left"
    if platform == "win32":
        return f"win+ctrl+{key}"
    if platform == "darwin":
        return f"ctrl+{key}"
    return f"super+page_{'down' if direction == 'next' else 'up'}"


def switch_desktop(direction="next"):
    combo = desktop_combo(direction, sys.platform)
    KeyboardController().press_combo(combo)
    return f"Switched to {direction} desktop"


def main():
    args = [arg for arg in sys.argv[1:] if arg != "--noop"]
    noop = "--noop" in sys.argv
    direction = args[0] if args and args[0] in ("next", "previous") else "next"
    print(f"Switching to {direction} desktop in 1s...")
    time.sleep(1)
    if noop:
        print("Dry run.")
        return
    print(switch_desktop(direction))


if __name__ == "__main__":
    sys.exit(main())
