import sys
import time

from skills._click_try import attempt_loop, click_candidates


def try_click(x, y, expect_text=None):
    points = click_candidates((x, y, 1, 1))
    return attempt_loop(points, expect_text)


def main():
    args = [arg for arg in sys.argv[1:] if arg != "--noop"]
    noop = "--noop" in sys.argv
    if len(args) < 2:
        print("Usage: python skills/try_click.py <x> <y> [expect text] [--noop]")
        return
    x, y = int(args[0]), int(args[1])
    expect = args[2] if len(args) > 2 else None
    print(f"Trying to click around ({x},{y})...")
    time.sleep(1)
    if noop:
        print("Dry run.")
        return
    print(try_click(x, y, expect))


if __name__ == "__main__":
    sys.exit(main())
