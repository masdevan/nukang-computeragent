import json
import re
import sys
import time

from app.services.device import collect_device_info, format_device_info
from skills import app_launcher, file_ops, keyboard_controls, ocr, screenshot, window_focus
from skills import close_app as close_app_skill
from skills import drag as drag_skill
from skills import find_and_click as find_and_click_skill
from skills import try_click as try_click_skill
from skills._mouse import current_position, click as mouse_click, move_to as mouse_move_to, scroll as mouse_scroll, xbutton

MAX_STEPS = 25
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

TOOLS = [
    {"name": "press_combo", "args": "combo string", "desc": "Press keyboard combination, e.g. win, alt+tab, ctrl+s, right*3"},
    {"name": "press_key", "args": "key string", "desc": "Press a single keyboard key, e.g. enter, esc, f5"},
    {"name": "type_text", "args": "text string", "desc": "Type text using the keyboard"},
    {"name": "launch_app", "args": "name string", "desc": "Launch an installed application by name, e.g. chrome, notepad, calculator"},
    {"name": "focus_window", "args": "title string", "desc": "Bring a window to the foreground and focus it, e.g. after launching an app, before clicking or typing into it"},
    {"name": "close_app", "args": "title string", "desc": "Close a window gracefully by its title, e.g. close_app(Notepad). Never use alt+f4"},
    {"name": "run_command", "args": "command string", "desc": "Run a Windows command line with arguments, e.g. chrome --profile-directory=\"Profile 1\""},
    {"name": "read_file", "args": "path string", "desc": "Read a text file and return its content. Use to inspect config files like Chrome's Local State to find profile folder names"},
    {"name": "move_to", "args": "x int, y int", "desc": "Move the mouse cursor to screen coordinates"},
    {"name": "move_by", "args": "dx int, dy int", "desc": "Move the mouse cursor by an offset from its current position"},
    {"name": "click", "args": "button string", "desc": "Click mouse button at the current cursor position: left, right, or middle"},
    {"name": "double_click", "args": "none", "desc": "Double click the left mouse button at the current cursor position"},
    {"name": "scroll", "args": "amount int", "desc": "Scroll the mouse wheel at the current cursor position, positive up, negative down. To read long content: move_to the list, scroll, capture_screen again, repeat until the text stops changing"},
    {"name": "drag", "args": "from_x int, from_y int, to_x int, to_y int", "desc": "Drag with the left mouse button from one point to another, like moving a window — use it to move blocking windows out of the way"},
    {"name": "find_and_click", "args": "target_text string, expect_text string optional, context_text string optional, app_name string optional", "desc": "Scroll until the text is visible, then try a list of click points around it until the expected result appears. context_text = text proving the dialog is still open (e.g. \"Who's using Chrome?\"); app_name = the app to reopen if the context gets lost — e.g. find_and_click(\"Devan Yudistira\", \"Devan Yudistira - Google Chrome\", \"Who's using Chrome?\", \"chrome\")"},
    {"name": "try_click", "args": "x int, y int, expect_text string optional", "desc": "Try a list of click points around (x,y) until the expected result appears or the list is exhausted — for precise clicks on any element"},
    {"name": "position", "args": "none", "desc": "Report the current mouse cursor position as x,y"},
    {"name": "back", "args": "none", "desc": "Press the mouse back button, e.g. browser back"},
    {"name": "forward", "args": "none", "desc": "Press the mouse forward button, e.g. browser forward"},
    {"name": "capture_screen", "args": "none", "desc": "Screenshot the FULL screen, saved automatically to the captures folder; you always use this one"},
    {"name": "list_windows", "args": "none", "desc": "List titles of visible windows"},
    {"name": "get_device_info", "args": "none", "desc": "Report OS, screen resolution with DPI scale, CPU, and RAM — use the resolution to plan mouse coordinates"},
]

SYSTEM_PROMPT = """You are Nukang, an AI computer agent that controls a Windows computer.
When the user asks you to do something on the computer, you ACTUALLY DO IT by calling a tool.
You are not limited to text answers: you have real control of the keyboard, mouse, and apps.
Always reply in {language}, regardless of the language the user types in.

To perform an action, reply with ONLY a JSON object, no other text:
{{"tool": {{"name": "<tool_name>", "args": {{...}}}}}}
Your tool call must be a single valid JSON object with properly escaped quotes, no prose around it.

Available tools:
{tools}

After each tool result, continue until the task is done.
Work efficiently: take ONE screenshot when you need to see the screen, do not repeat the same screenshot, and verify results with at most one capture.
After taking a screenshot, you receive its text content with screen coordinates, e.g. "Devan Yudistira" at (960, 40).
Use this to find elements: move_to the element's coordinates, then click — behave like a human using the computer.

When the content on screen is long (OCR shows many lines or "truncated"): do NOT decide yet.
Scroll through ALL of it first: move_to the middle of the content, scroll with a negative amount,
capture_screen again, and repeat until the OCR text repeats or stops changing (bottom reached).
Only then make your decision. Never decide from the first screenful alone. This is mandatory — the user will verify you read everything.

INTERACTION PRIORITY — every action that can use the mouse uses the mouse first:
1. Mouse: take a FULL SCREEN screenshot with capture_screen, read the OCR coordinates (always absolute to the screen), move the mouse with move_to, then click / double_click / scroll at its position. Use this for buttons, menus, tabs, profiles, links — anything visible on screen.
2. Keyboard: press_combo and type_text for typing text and shortcuts like ctrl+c or win — but ALWAYS click into the target field/area with the mouse first to give it focus.
3. Commands: launch_app and run_command ONLY as a fallback when mouse or keyboard cannot do the job, or for opening apps.
When the user asks to interact with something on screen, NEVER jump straight to a command — screenshot first, then click it with the mouse.
To click an element whose text you know, use find_and_click(text, expected_result, context_text, app_name) — it scrolls, tries a list of click points, and if the context gets lost it presses Esc, then reopens the app and continues.
The Nukang app window is moved to the bottom-right corner during scanning so it never covers what you inspect — understand this and rely on it.
The app is also moved aside automatically before every screenshot and scroll — you never need to think about it or mention it.
When find_and_click returns success, the task is done — do not run extra verification steps.
For precise clicks on coordinates, use try_click(x, y, expected_result) — it tries the surrounding points until something changes.
If a window closes after a click, recover: press Esc, then re-open the app if needed, and continue. Never ask the user for environment details.
Plan your attempt list silently. Execute attempts back-to-back; do not narrate every step. Report only the final result and what was tried.
If any window (including the Nukang app) blocks the target, drag it out of the way with drag() — or the app moves itself automatically.
After launching an app, ALWAYS bring it to focus with focus_window before clicking or typing into it.
To close an app, use close_app(title) — never alt+f4.
You ALWAYS screenshot the full screen — there is no window-only capture. OCR coordinates are always absolute screen coordinates.

read_file reads files for you — NEVER use run_command or launch_app to read or open files; run_command is only for launching apps with arguments.
Before asking the user for information, find it yourself: read_file and list_windows can answer most questions. Ask the user only as a last resort.
When the task is finished (or needs no tool), reply in plain text, briefly describing what you did.
Never say you cannot physically do something on this computer.
You may call at most {max_steps} tools per task."""


def build_system_prompt(language):
    return SYSTEM_PROMPT.format(
        language=language,
        tools=chr(10).join(f'- {t["name"]}({t["args"]}): {t["desc"]}' for t in TOOLS),
        max_steps=MAX_STEPS,
    )


def parse_tool_call(text):
    candidates = extract_json_blocks(text)
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        tool = payload.get("tool")
        if isinstance(tool, dict) and isinstance(tool.get("name"), str):
            return tool
    return None


def extract_json_blocks(text):
    stripped = re.sub(r"```(?:json)?\s*|\s*```", "", text)
    candidates = []
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", stripped):
        try:
            payload, _ = decoder.raw_decode(stripped, match.start())
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            candidates.append(json.dumps(payload))
    if stripped not in candidates:
        candidates.append(stripped)
    return candidates


def looks_like_tool_attempt(text):
    return '"tool"' in text and ('"name"' in text or '"args"' in text)


def format_call(tool_call):
    args = tool_call.get("args", {})
    return f"{tool_call['name']}({', '.join(f'{k}={v}' for k, v in args.items())})"


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


def close_app(args):
    return close_app_skill.close_app(args["title"], protected_hwnd=MAIN_WINDOW_HWND)


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
    screen_size = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
    new_x, new_y = choose_app_position(app_rect, (x, y), screen_size)
    move_window(new_x, new_y)
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
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    move_window(screen_width - width - 8, screen_height - height - 8)
    time.sleep(0.1)


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


def capture_screen(args):
    reposition_app_to_corner()
    capture = screenshot.ScreenshotCapture()
    path = capture.capture_screen()
    text = ocr.write_ocr_sidecar(path)
    result = f"Saved: {path}\n{text}"
    if "truncated" in text:
        result += (
            "\nIMPORTANT: the OCR above was truncated — the content continues below the visible screen. "
            "You MUST scroll down (move_to the middle of the content, then scroll with a negative amount), "
            "capture_screen again, and repeat until the text stops changing, before making any decision."
        )
    return result


def list_windows(args):
    return "\n".join(screenshot.ScreenshotCapture().list_windows())


def get_device_info(args):
    return format_device_info(collect_device_info())


EXECUTORS = {
    "press_combo": press_combo,
    "press_key": press_key,
    "type_text": type_text,
    "launch_app": launch_app,
    "focus_window": focus_window,
    "close_app": close_app,
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
    "list_windows": list_windows,
    "get_device_info": get_device_info,
}
