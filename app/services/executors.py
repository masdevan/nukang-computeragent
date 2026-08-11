from app.services.device import collect_device_info, format_device_info
from app.services.window_manager import (
    MAIN_WINDOW_HWND, reposition_app_away, reposition_app_to_corner,
)
from skills import app_launcher, file_ops, keyboard_controls, ocr, screenshot, window_focus
from skills import app_refocus as app_refocus_skill
from skills import close_app as close_app_skill
from skills import drag as drag_skill
from skills import expand_window as expand_window_skill
from skills import find_and_click as find_and_click_skill
from skills import minimize_window as minimize_window_skill
from skills import switch_app as switch_app_skill
from skills import switch_desktop as switch_desktop_skill
from skills import try_click as try_click_skill
from skills._mouse import current_position, click as mouse_click, move_to as mouse_move_to, scroll as mouse_scroll, xbutton


def recall_observations(args):
    from skills.screenshot import current_session

    return ocr.session_ocr_texts(current_session(), args.get("limit"))


def list_apps(args):
    from app.services.apps import cached_installed_apps

    return "\n".join(cached_installed_apps())


def execute_tool(tool_call):
    name = tool_call["name"]
    args = tool_call.get("args", {})
    executor = EXECUTORS.get(name)
    if executor is None:
        return f"Unknown tool: {name}"
    try:
        result = executor(args)
        return result if result is not None else "ok"
    except Exception as error:
        return f"Tool failed: {error}"


def press_combo(args):
    return keyboard_controls.KeyboardController().press_combo(args["combo"])


def press_key(args):
    keyboard_controls.KeyboardController().press_key(args["key"])


def type_text(args):
    keyboard_controls.KeyboardController().type_text(args["text"])


def launch_app(args):
    return app_launcher.launch_app(args["name"])


def focus_window(args):
    return window_focus.focus_window(args["title"])


def app_refocus(args):
    return app_refocus_skill.app_refocus(args["title"], protected_hwnd=MAIN_WINDOW_HWND)


def close_app(args):
    return close_app_skill.close_app(args["title"], protected_hwnd=MAIN_WINDOW_HWND)


def expand_window(args):
    return expand_window_skill.expand_window(args["title"], protected_hwnd=MAIN_WINDOW_HWND)


def minimize_window(args):
    return minimize_window_skill.minimize_window(args["title"], protected_hwnd=MAIN_WINDOW_HWND)


def hide_window(args):
    return minimize_window_skill.hide_window(args["title"], protected_hwnd=MAIN_WINDOW_HWND)


def switch_app(args):
    return switch_app_skill.switch_app(args.get("direction", "next"))


def switch_desktop(args):
    return switch_desktop_skill.switch_desktop(args.get("direction", "next"))


def run_command(args):
    return app_launcher.run_command(args["command"])


def read_file(args):
    return file_ops.read_file(args["path"])


def move_to(args):
    x, y = int(args["x"]), int(args["y"])
    reposition_app_away(x, y)
    mouse_move_to(x, y)
    return f"Mouse moved to ({x},{y})"


def move_by(args):
    x, y = current_position()
    target_x = x + int(args["dx"])
    target_y = y + int(args["dy"])
    reposition_app_away(target_x, target_y)
    mouse_move_to(target_x, target_y)
    return f"Mouse moved by {args['dx']},{args['dy']}"


def click(args):
    x, y = current_position()
    reposition_app_away(x, y)
    button = args.get("button", "left")
    mouse_click(button, x, y)
    return f"Clicked {button} at ({x},{y})"


def double_click(args):
    x, y = current_position()
    reposition_app_away(x, y)
    mouse_click("left", x, y, clicks=2, interval=0.05)
    return f"Double clicked at ({x},{y})"


def scroll(args):
    x, y = current_position()
    reposition_app_to_corner()
    mouse_scroll(int(args["amount"]), x, y)
    return f"Scrolled at ({x},{y})"


def drag(args):
    return drag_skill.drag(
        int(args["from_x"]), int(args["from_y"]),
        int(args["to_x"]), int(args["to_y"]),
    )


def find_and_click(args):
    return find_and_click_skill.find_and_click(
        args["target_text"],
        args.get("expect_text"),
        args.get("context_text"),
        args.get("app_name"),
    )


def try_click(args):
    return try_click_skill.try_click(
        int(args["x"]), int(args["y"]), args.get("expect_text"),
    )


def position(args):
    x, y = current_position()
    return f"Mouse position: {x},{y}"


def back(args):
    xbutton("back")


def forward(args):
    xbutton("forward")


def capture_screen(args):
    reposition_app_to_corner()
    capture = screenshot.ScreenshotCapture()
    path = capture.capture_screen(region=capture_region())
    text = ocr.write_ocr_sidecar(path)
    result = f"Saved: {path}\n{text}"
    if "truncated" in text:
        result += (
            "\nIMPORTANT: the OCR above was truncated — the content continues below the visible screen. "
            "You MUST scroll down (move_to the middle of the content, then scroll with a negative amount), "
            "capture_screen again, and repeat until the text stops changing, before making any decision."
        )
    return result


def capture_region():
    from app.services.device import active_screen_info

    monitor = active_screen_info()
    if monitor is None:
        return None
    return (
        monitor["x"], monitor["y"],
        monitor["width"], monitor["height"],
    )


def list_windows(args):
    return "\n".join(screenshot.ScreenshotCapture().list_windows())


def list_desktops(args):
    from app.services.device import virtual_desktops

    result = virtual_desktops()
    if result is None:
        return "Virtual desktop listing is only supported on Windows."
    desktops, current = result
    if not desktops:
        return "No desktops detected."
    lines = []
    for index, (desktop_id, titles) in enumerate(desktops.items(), start=1):
        marker = " (active)" if desktop_id == current else ""
        lines.append(f"Desktop {index}{marker}: {len(titles)} windows")
    return "\n".join(lines)


def get_device_info(args):
    return format_device_info(collect_device_info())


EXECUTORS = {
    "press_combo": press_combo,
    "press_key": press_key,
    "type_text": type_text,
    "launch_app": launch_app,
    "focus_window": focus_window,
    "app_refocus": app_refocus,
    "close_app": close_app,
    "expand_window": expand_window,
    "minimize_window": minimize_window,
    "hide_window": hide_window,
    "switch_app": switch_app,
    "switch_desktop": switch_desktop,
    "run_command": run_command,
    "read_file": read_file,
    "move_to": move_to,
    "move_by": move_by,
    "click": click,
    "double_click": double_click,
    "scroll": scroll,
    "drag": drag,
    "find_and_click": find_and_click,
    "try_click": try_click,
    "position": position,
    "back": back,
    "forward": forward,
    "capture_screen": capture_screen,
    "recall_observations": recall_observations,
    "list_apps": list_apps,
    "list_windows": list_windows,
    "list_desktops": list_desktops,
    "get_device_info": get_device_info,
}
