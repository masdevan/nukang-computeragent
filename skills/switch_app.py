import sys
import time

from skills.keyboard_controls import KeyboardController

COMBOS = {
    "next": "alt+tab",
    "previous": "alt+shift+tab",
}


def switch_app(direction="next"):
    combo = COMBOS.get(direction, COMBOS["next"])
    KeyboardController().press_combo(combo)
    return f"Switched to {direction} app"


def main():
    args = [arg for arg in sys.argv[1:] if arg != "--noop"]
    noop = "--noop" in sys.argv
    direction = args[0] if args and args[0] in ("next", "previous") else "next"
    print(f"Switching to {direction} app in 1s...")
    time.sleep(1)
    if noop:
        print("Dry run.")
        return
    print(switch_app(direction))


if __name__ == "__main__":
    sys.exit(main())
