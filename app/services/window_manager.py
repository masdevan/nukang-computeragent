import sys
import time

MAIN_WINDOW_HWND = None


def set_main_window(hwnd):
    global MAIN_WINDOW_HWND
    MAIN_WINDOW_HWND = hwnd


def main_window_rect():
    if MAIN_WINDOW_HWND is None or sys.platform != "win32":
        return None
    import ctypes
    from ctypes import wintypes

    rect = wintypes.RECT()
    ctypes.windll.user32.GetWindowRect(MAIN_WINDOW_HWND, ctypes.byref(rect))
    return (rect.left, rect.top, rect.right, rect.bottom)


def choose_app_position(app_rect, point, screen_size):
    app_width = app_rect[2] - app_rect[0]
    app_height = app_rect[3] - app_rect[1]
    margin = 8
    point_x, point_y = point
    screen_width, screen_height = screen_size
    options = {
        "top-left": (margin, margin),
        "top-right": (screen_width - app_width - margin, margin),
        "bottom-left": (margin, screen_height - app_height - margin),
        "bottom-right": (screen_width - app_width - margin, screen_height - app_height - margin),
    }
    opposite_quadrant = {
        "top-left": "bottom-right",
        "top-right": "bottom-left",
        "bottom-left": "top-right",
        "bottom-right": "top-left",
    }
    if point_x < screen_width / 2 and point_y < screen_height / 2:
        point_quadrant = "top-left"
    elif point_x >= screen_width / 2 and point_y < screen_height / 2:
        point_quadrant = "top-right"
    elif point_x < screen_width / 2:
        point_quadrant = "bottom-left"
    else:
        point_quadrant = "bottom-right"
    preferred = opposite_quadrant[point_quadrant]
    free_options = {
        name: position
        for name, position in options.items()
        if not (
            position[0] <= point_x <= position[0] + app_width
            and position[1] <= point_y <= position[1] + app_height
        )
    }
    if preferred in free_options:
        return options[preferred]
    if free_options:
        farthest = max(
            free_options.items(),
            key=lambda item: (item[1][0] - point_x) ** 2 + (item[1][1] - point_y) ** 2,
        )[1]
        return farthest
    return options[preferred]


def reposition_app_away(x, y):
    if not window_handle_valid():
        return
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    rect = wintypes.RECT()
    user32.GetWindowRect(MAIN_WINDOW_HWND, ctypes.byref(rect))
    app_rect = (rect.left, rect.top, rect.right, rect.bottom)
    if not (app_rect[0] <= x <= app_rect[2] and app_rect[1] <= y <= app_rect[3]):
        return
    screen = active_screen()
    new_x, new_y = choose_app_position(app_rect, (x, y), screen)
    move_window(new_x, new_y)
    follow_active_desktop()
    time.sleep(0.1)


def reposition_app_to_corner():
    if not window_handle_valid():
        return
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    rect = wintypes.RECT()
    user32.GetWindowRect(MAIN_WINDOW_HWND, ctypes.byref(rect))
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    screen = active_screen()
    screen_width, screen_height = screen
    move_window(screen_width - width - 8, screen_height - height - 8)
    follow_active_desktop()
    time.sleep(0.1)


def active_screen():
    from app.services.device import active_screen_info

    monitor = active_screen_info()
    if monitor is None:
        import ctypes

        user32 = ctypes.windll.user32
        return (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
    return (monitor["width"], monitor["height"])


def follow_active_desktop():
    if MAIN_WINDOW_HWND is None or sys.platform != "win32":
        return
    try:
        from app.services.device import (
            current_desktop_guid, desktop_manager,
            manager_move_window_to_desktop, release_manager,
        )

        manager = desktop_manager()
        if manager is None:
            return
        try:
            desktop_id = current_desktop_guid()
            if desktop_id:
                manager_move_window_to_desktop(manager, MAIN_WINDOW_HWND, desktop_id)
        finally:
            release_manager(manager)
    except Exception:
        pass


def window_handle_valid():
    if MAIN_WINDOW_HWND is None or sys.platform != "win32":
        return False
    import ctypes

    return bool(ctypes.windll.user32.IsWindow(MAIN_WINDOW_HWND))


def move_window(x, y):
    import ctypes

    user32 = ctypes.windll.user32
    result = user32.SetWindowPos(
        MAIN_WINDOW_HWND, -1,
        x, y, 0, 0,
        0x0001 | 0x0010 | 0x0040,
    )
    if result == 0:
        user32.MoveWindow(MAIN_WINDOW_HWND, x, y, 0, 0, True)
