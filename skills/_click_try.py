import sys
import time

from skills import ocr
from skills._mouse import click as mouse_click, current_position, move_to as mouse_move_to, scroll as mouse_scroll
from skills.screenshot import ScreenshotCapture

MAX_PHASE_ITERATIONS = 8
SCROLL_NOTCHES = 4
FINGERPRINT_CHARS = 300
CLICK_SLEEP = 0.2
CORNER_INSET = 10


def click_candidates(box):
    left, top, width, height = box
    center_x = left + width // 2
    center_y = top + height // 2
    offset_x = max(4, min(14, width // 4))
    offset_y = max(4, min(14, height // 4))
    points = [
        (center_x, center_y),
        (center_x + offset_x, center_y),
        (center_x - offset_x, center_y),
        (center_x, center_y + offset_y),
        (center_x, center_y - offset_y),
    ]
    if width > 80 and height > 40:
        points.append((left + CORNER_INSET, top + CORNER_INSET))
        points.append((left + width - CORNER_INSET, top + height - CORNER_INSET))
    import pyautogui

    screen_width, screen_height = pyautogui.size()
    seen = set()
    result = []
    for x, y in points:
        clamped = (max(0, min(x, screen_width - 1)), max(0, min(y, screen_height - 1)))
        if clamped not in seen:
            seen.add(clamped)
            result.append(clamped)
    return result


def attempt_loop(points, expect_text, context=None, on_context_lost=None):
    attempts = []
    before_texts = line_texts(capture_lines())
    for index, (x, y) in enumerate(points, start=1):
        move_to(x, y)
        time.sleep(CLICK_SLEEP)
        click()
        time.sleep(CLICK_SLEEP)
        if verify_success(expect_text, before_texts, context):
            return f"Attempt {index}/{len(points)}: clicked ({x},{y}) -> success"
        if on_context_lost is not None and on_context_lost():
            break
        attempts.append(f"Attempt {index}/{len(points)}: clicked ({x},{y}) -> no change")
    return "All attempts failed:\n" + "\n".join(attempts)


def context_still_open(context):
    lines = capture_lines()
    if lines is None:
        return False
    return any(context in text.lower() for text, box, center, words in lines)


def verify_success(expect_text, before_texts, context=None):
    lines = capture_lines()
    if lines is None:
        return False
    if expect_text:
        if any(expect_text.lower() in text.lower() for text, box, center, words in lines):
            return True
        return window_title_matches(expect_text)
    after_texts = line_texts(lines)
    if context:
        if not any(context in text.lower() for text, box, center, words in lines):
            return False
        return bool(after_texts - before_texts)
    return bool(after_texts - before_texts)


def window_title_matches(expect_text):
    try:
        from skills.screenshot import ScreenshotCapture

        titles = ScreenshotCapture().list_windows()
    except Exception:
        return False
    return any(expect_text.lower() in title.lower() for title in titles)


def line_texts(lines):
    if lines is None:
        return set()
    return {text for text, box, center, words in lines}


def fingerprint_lines(lines):
    if lines is None:
        return None
    return "\n".join(text for text, box, center, words in lines)[:FINGERPRINT_CHARS]


def capture_lines():
    import pyautogui

    from io import BytesIO

    buffer = BytesIO()
    pyautogui.screenshot().save(buffer, format="PNG")
    return ocr.ocr_image(buffer.getvalue())


def find_target(lines, wanted):
    app_rect = get_app_rect()
    for text, box, center, words in lines:
        for word_text, word_box, word_center in words:
            if wanted in word_text.lower() and not inside_app(word_center, app_rect):
                return word_box
        if wanted in text.lower() and not inside_app(center, app_rect):
            return box
    return None


def inside_app(point, app_rect):
    if app_rect is None:
        return False
    x, y = point
    left, top, right, bottom = app_rect
    return left <= x <= right and top <= y <= bottom


def get_app_rect():
    try:
        from app.services.tools import main_window_rect

        return main_window_rect()
    except ImportError:
        return None


def move_to(x, y):
    reposition(x, y)
    mouse_move_to(x, y)


def click():
    x, y = current_position()
    reposition(x, y)
    mouse_click("left", x, y)


def reposition(x, y):
    try:
        from app.services.tools import reposition_app_away

        reposition_app_away(x, y)
    except ImportError:
        pass


def scroll(direction):
    import pyautogui

    width, height = pyautogui.size()
    move_to(width // 2, height // 2)
    mouse_scroll(direction, width // 2, height // 2)
    time.sleep(0.2)


def scan_direction(wanted, direction):
    previous_fingerprint = None
    for _ in range(MAX_PHASE_ITERATIONS):
        lines = capture_lines()
        if lines is None:
            return None
        box = find_target(lines, wanted)
        if box is not None:
            return box
        fingerprint = fingerprint_lines(lines)
        if fingerprint == previous_fingerprint:
            return None
        previous_fingerprint = fingerprint
        scroll(direction)
    return None
