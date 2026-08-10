import sys
import time

from skills._mouse import xbutton

CLICK_DELAY = 1


def main():
    noop = "--noop" in sys.argv
    print(f"Mouse forward button in {CLICK_DELAY}s...")
    time.sleep(CLICK_DELAY)
    if noop:
        print("Dry run, nothing pressed.")
        return
    xbutton("forward")
    print("Forward done.")


if __name__ == "__main__":
    sys.exit(main())
