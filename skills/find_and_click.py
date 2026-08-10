import sys
import time

from skills._click_try import (
    attempt_loop, click_candidates, context_still_open, scan_direction,
)
from skills._mouse import click as mouse_click, current_position, move_to as mouse_move_to
from skills.keyboard_controls import KeyboardController
from skills.screenshot import ScreenshotCapture

SCROLL_NOTCHES = 4
RECOVERY_ROUNDS = 2


def find_and_click(target_text, expect_text=None, context_text=None, app_name=None):
    wanted = target_text.lower()
    context = context_text.lower() if context_text else None
    reposition_corner()
    for _ in range(RECOVERY_ROUNDS):
        box = locate(wanted)
        if box is None:
            return f"'{target_text}' not found on screen"
        points = click_candidates(box)

        def context_lost():
            if context and not context_still_open(context):
                return True
            return False

        result = attempt_loop(points, expect_text, context=context, on_context_lost=context_lost)
        if "success" in result:
            return result
        if context and not context_still_open(context):
            if not recover(wanted, app_name):
                return f"Context lost and could not be recovered. Re-open the app and try again.\n{result}"
            continue
        return result
    return f"'{target_text}' not found on screen"


def reposition_corner():
    try:
        from app.services.tools import reposition_app_to_corner

        reposition_app_to_corner()
    except ImportError:
        pass


def locate(wanted):
    box = scan_direction(wanted, -SCROLL_NOTCHES)
    if box is None:
        box = scan_direction(wanted, SCROLL_NOTCHES)
    return box


def recover(wanted, app_name):
    KeyboardController().press_combo("esc")
    time.sleep(0.4)
    if locate(wanted) is not None:
        return True
    if app_name:
        from skills import app_launcher, app_refocus, close_app

        app_refocus.app_refocus(app_name)
        time.sleep(0.5)
        if locate(wanted) is not None:
            return True
        close_app.close_app(app_name)
        time.sleep(0.5)
        app_launcher.launch_app(app_name)
        time.sleep(1.5)
        return locate(wanted) is not None
    return False


def main():
    args = [arg for arg in sys.argv[1:] if arg != "--noop"]
    noop = "--noop" in sys.argv
    if len(args) < 1:
        print("Usage: python skills/find_and_click.py <target> [expect] [context] [app] [--noop]")
        return
    target = args[0]
    expect = args[1] if len(args) > 1 else None
    context = args[2] if len(args) > 2 else None
    app_name = args[3] if len(args) > 3 else None
    print(f"Searching for '{target}'...")
    time.sleep(1)
    if noop:
        print("Dry run.")
        return
    print(find_and_click(target, expect, context, app_name))


if __name__ == "__main__":
    sys.exit(main())
