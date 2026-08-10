import json
import re

from app.services.device import collect_device_info, format_device_info
from skills import app_launcher, file_ops, keyboard_controls, mouse_control, ocr, screenshot
from skills.virtual_cursor import VirtualCursor

MAX_STEPS = 15
VIRTUAL_CURSOR = None

TOOLS = [
    {"name": "press_combo", "args": "combo string", "desc": "Press keyboard combination, e.g. win, alt+tab, ctrl+s, right*3"},
    {"name": "press_key", "args": "key string", "desc": "Press a single keyboard key, e.g. enter, esc, f5"},
    {"name": "type_text", "args": "text string", "desc": "Type text using the keyboard"},
    {"name": "launch_app", "args": "name string", "desc": "Launch an installed application by name, e.g. chrome, notepad, calculator"},
    {"name": "run_command", "args": "command string", "desc": "Run a Windows command line with arguments, e.g. chrome --profile-directory=\"Profile 1\""},
    {"name": "read_file", "args": "path string", "desc": "Read a text file and return its content. Use to inspect config files like Chrome's Local State to find profile folder names"},
    {"name": "move_to", "args": "x int, y int", "desc": "Move the mouse cursor to screen coordinates"},
    {"name": "move_by", "args": "dx int, dy int", "desc": "Move the mouse cursor by an offset from its current position"},
    {"name": "click", "args": "button string", "desc": "Click mouse button at current position: left, right, or middle"},
    {"name": "double_click", "args": "none", "desc": "Double click the left mouse button at the current position"},
    {"name": "scroll", "args": "amount int", "desc": "Scroll the mouse wheel, positive up, negative down"},
    {"name": "position", "args": "none", "desc": "Report the current mouse cursor position as x,y"},
    {"name": "back", "args": "none", "desc": "Press the mouse back button, e.g. browser back"},
    {"name": "forward", "args": "none", "desc": "Press the mouse forward button, e.g. browser forward"},
    {"name": "capture_screen", "args": "none", "desc": "Screenshot the full screen, saved automatically to the captures folder"},
    {"name": "capture_window", "args": "title string", "desc": "Screenshot a window whose title contains the given text, saved automatically to the captures folder"},
    {"name": "list_windows", "args": "none", "desc": "List titles of visible windows"},
    {"name": "get_device_info", "args": "none", "desc": "Report OS, screen resolution with DPI scale, CPU, and RAM — use the resolution to plan mouse coordinates"},
    {"name": "show_virtual_cursor", "args": "x int, y int", "desc": "Show an orange pointer at screen coordinates to direct the user's attention"},
    {"name": "hide_virtual_cursor", "args": "none", "desc": "Hide the orange virtual cursor overlay"},
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

INTERACTION PRIORITY — use the mouse first, always:
1. Mouse: take a screenshot, read the OCR coordinates, move_to the element, then click / double_click / scroll. Use this for buttons, menus, tabs, profiles, links — anything visible on screen.
2. Keyboard: press_combo and type_text for typing text and shortcuts like ctrl+c or win.
3. Commands: launch_app and run_command ONLY as a fallback when mouse or keyboard cannot do the job, or for opening apps.
When the user asks to interact with something on screen, NEVER jump straight to a command — screenshot first, then click it with the mouse.

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


def run_command(args):
    return app_launcher.run_command(args["command"])


def read_file(args):
    return file_ops.read_file(args["path"])


def move_to(args):
    mouse_control.MouseController().move_to(int(args["x"]), int(args["y"]))


def move_by(args):
    mouse_control.MouseController().move_by(int(args["dx"]), int(args["dy"]))


def click(args):
    mouse_control.MouseController().click(args.get("button", "left"))


def double_click(args):
    mouse_control.MouseController().double_click()


def scroll(args):
    mouse_control.MouseController().scroll(int(args["amount"]))


def position(args):
    pos = mouse_control.MouseController().position()
    return f"Mouse position: {pos.x},{pos.y}"


def back(args):
    mouse_control.MouseController().back()


def forward(args):
    mouse_control.MouseController().forward()


def capture_screen(args):
    capture = screenshot.ScreenshotCapture()
    path = capture.capture_screen()
    return f"Saved: {path}\n{ocr.write_ocr_sidecar(path)}"


def capture_window(args):
    capture = screenshot.ScreenshotCapture()
    path = capture.capture_window(args["title"])
    if path is None:
        return "Window not found"
    return f"Saved: {path}\n{ocr.write_ocr_sidecar(path)}"


def list_windows(args):
    return "\n".join(screenshot.ScreenshotCapture().list_windows())


def get_device_info(args):
    return format_device_info(collect_device_info())


def show_virtual_cursor(args):
    cursor = get_virtual_cursor()
    cursor.show_cursor(int(args["x"]), int(args["y"]))
    return f"Virtual cursor shown at {args['x']},{args['y']}"


def hide_virtual_cursor(args):
    get_virtual_cursor().hide_cursor()
    return "Virtual cursor hidden"


def get_virtual_cursor():
    global VIRTUAL_CURSOR
    if VIRTUAL_CURSOR is None:
        VIRTUAL_CURSOR = VirtualCursor(keyboard_control=False)
    return VIRTUAL_CURSOR


EXECUTORS = {
    "press_combo": press_combo,
    "press_key": press_key,
    "type_text": type_text,
    "launch_app": launch_app,
    "run_command": run_command,
    "read_file": read_file,
    "move_to": move_to,
    "move_by": move_by,
    "click": click,
    "double_click": double_click,
    "scroll": scroll,
    "position": position,
    "back": back,
    "forward": forward,
    "capture_screen": capture_screen,
    "capture_window": capture_window,
    "list_windows": list_windows,
    "get_device_info": get_device_info,
    "show_virtual_cursor": show_virtual_cursor,
    "hide_virtual_cursor": hide_virtual_cursor,
}
