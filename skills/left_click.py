import sys
import time

from skills._mouse import click

CLICK_DELAY = 1


def main():
    args = [arg for arg in sys.argv[1:] if arg != "--noop"]
    noop = "--noop" in sys.argv
    x, y = None, None
    if len(args) == 2:
        x, y = int(args[0]), int(args[1])
    target = f"({x}, {y})" if x is not None else "(current cursor position)"
    print(f"Left click at {target} in {CLICK_DELAY}s... move the mouse if needed.")
    time.sleep(CLICK_DELAY)
    if noop:
        print("Dry run, nothing clicked.")
        return
    click("left", x, y)
    print("Left click done.")


if __name__ == "__main__":
    sys.exit(main())
