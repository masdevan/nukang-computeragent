import sys
import time

from skills.general._mouse import mouse_down, mouse_up, move_to

DRAG_STEPS = 12


def drag(from_x, from_y, to_x, to_y):
    move_to(from_x, from_y, smooth=False)
    time.sleep(0.05)
    mouse_down("left")
    time.sleep(0.05)
    for step in range(1, DRAG_STEPS + 1):
        ratio = step / DRAG_STEPS
        move_to(
            round(from_x + (to_x - from_x) * ratio),
            round(from_y + (to_y - from_y) * ratio),
            smooth=False,
        )
        time.sleep(0.01)
    time.sleep(0.05)
    mouse_up("left")
    return f"Dragged from ({from_x},{from_y}) to ({to_x},{to_y})"


def main():
    args = [arg for arg in sys.argv[1:] if arg != "--noop"]
    noop = "--noop" in sys.argv
    if len(args) != 4:
        print("Usage: python skills/drag.py <from_x> <from_y> <to_x> <to_y> [--noop]")
        return
    from_x, from_y, to_x, to_y = (int(arg) for arg in args)
    print(f"Dragging from ({from_x},{from_y}) to ({to_x},{to_y}) in 1s...")
    time.sleep(1)
    if noop:
        print("Dry run, nothing dragged.")
        return
    print(drag(from_x, from_y, to_x, to_y))


if __name__ == "__main__":
    sys.exit(main())
