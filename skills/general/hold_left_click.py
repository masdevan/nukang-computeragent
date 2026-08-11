import sys
import time

from skills.general._mouse import hold

CLICK_DELAY = 1
HOLD_SECONDS = 1


def main():
    args = [arg for arg in sys.argv[1:] if arg != "--noop"]
    noop = "--noop" in sys.argv
    x, y = None, None
    if len(args) == 2:
        x, y = int(args[0]), int(args[1])
    target = f"({x}, {y})" if x is not None else "(current cursor position)"
    print(f"Hold left click at {target} for {HOLD_SECONDS}s in {CLICK_DELAY}s...")
    time.sleep(CLICK_DELAY)
    if noop:
        print("Dry run, nothing clicked.")
        return
    hold("left", x, y, seconds=HOLD_SECONDS)
    print("Hold done.")


if __name__ == "__main__":
    sys.exit(main())
