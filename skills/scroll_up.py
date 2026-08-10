import sys
import time

from skills._mouse import scroll

CLICK_DELAY = 1
DEFAULT_NOTCHES = 3


def main():
    args = [arg for arg in sys.argv[1:] if arg != "--noop"]
    noop = "--noop" in sys.argv
    amount = DEFAULT_NOTCHES
    if len(args) == 1:
        amount = int(args[0])
    print(f"Scroll up {amount} notch(es) in {CLICK_DELAY}s...")
    time.sleep(CLICK_DELAY)
    if noop:
        print("Dry run, nothing scrolled.")
        return
    scroll(amount)
    print("Scroll up done.")


if __name__ == "__main__":
    sys.exit(main())
