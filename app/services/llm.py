import json
import re

from PySide6.QtCore import QThread, Signal

from skills import app_launcher, keyboard_controls, mouse_control, screenshot
from skills.virtual_cursor import VirtualCursor

MAX_STEPS = 6
VIRTUAL_CURSOR = None

TOOLS = [
    {"name": "press_combo", "args": "combo string", "desc": "Press keyboard combination, e.g. win, alt+tab, ctrl+s, right*3"},
    {"name": "press_key", "args": "key string", "desc": "Press a single keyboard key, e.g. enter, esc, f5"},
    {"name": "type_text", "args": "text string", "desc": "Type text using the keyboard"},
    {"name": "launch_app", "args": "name string", "desc": "Launch an installed application by name, e.g. chrome, notepad, calculator"},
    {"name": "move_to", "args": "x int, y int", "desc": "Move the mouse cursor to screen coordinates"},
    {"name": "move_by", "args": "dx int, dy int", "desc": "Move the mouse cursor by an offset from its current position"},
    {"name": "click", "args": "button string", "desc": "Click mouse button at current position: left, right, or middle"},
    {"name": "double_click", "args": "none", "desc": "Double click the left mouse button at the current position"},
    {"name": "scroll", "args": "amount int", "desc": "Scroll the mouse wheel, positive up, negative down"},
    {"name": "position", "args": "none", "desc": "Report the current mouse cursor position as x,y"},
    {"name": "back", "args": "none", "desc": "Press the mouse back button, e.g. browser back"},
    {"name": "forward", "args": "none", "desc": "Press the mouse forward button, e.g. browser forward"},
    {"name": "capture_screen", "args": "file string", "desc": "Screenshot the full screen and save to file"},
    {"name": "capture_window", "args": "title string, file string", "desc": "Screenshot a window whose title contains the given text"},
    {"name": "list_windows", "args": "none", "desc": "List titles of visible windows"},
    {"name": "show_virtual_cursor", "args": "x int, y int", "desc": "Show an orange pointer at screen coordinates to direct the user's attention"},
    {"name": "hide_virtual_cursor", "args": "none", "desc": "Hide the orange virtual cursor overlay"},
]

SYSTEM_PROMPT = f"""You are Nukang, an AI computer agent that controls a Windows computer.
When the user asks you to do something on the computer, you ACTUALLY DO IT by calling a tool.
You are not limited to text answers: you have real control of the keyboard, mouse, and apps.
Reply in the language the user uses.

To perform an action, reply with ONLY a JSON object, no other text:
{{"tool": {{"name": "<tool_name>", "args": {{...}}}}}}

Available tools:
{chr(10).join(f'- {t["name"]}({t["args"]}): {t["desc"]}' for t in TOOLS)}

After each tool result, continue until the task is done.
When the task is finished (or needs no tool), reply in plain text, briefly describing what you did.
Never say you cannot physically do something on this computer.
You may call at most {MAX_STEPS} tools per task."""


class ChatAgent:
    def __init__(self, base_url, api_key, model):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model

    def build_client(self):
        import openai

        return openai.OpenAI(base_url=self.base_url, api_key=self.api_key)

    def reply(self, messages):
        client = self.build_client()
        completion = client.chat.completions.create(model=self.model, messages=messages)
        return completion.choices[0].message.content


class ToolAgent(ChatAgent):
    def reply(self, messages):
        conversation = [{"role": "system", "content": SYSTEM_PROMPT}, *messages]
        client = self.build_client()
        trace = []
        for _ in range(MAX_STEPS):
            completion = client.chat.completions.create(model=self.model, messages=conversation)
            text = completion.choices[0].message.content
            tool_call = parse_tool_call(text)
            if tool_call is None:
                return text, trace
            trace.append(format_call(tool_call))
            result = execute_tool(tool_call)
            conversation.append({"role": "assistant", "content": text})
            conversation.append({"role": "user", "content": f"Tool result: {result}"})
        return "Task stopped after too many steps.", trace


def parse_tool_call(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        payload = json.loads(match.group())
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    tool = payload.get("tool")
    if isinstance(tool, dict) and isinstance(tool.get("name"), str):
        return tool
    return None


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
    return screenshot.ScreenshotCapture().capture_screen(args.get("file", "screenshot.png"))


def capture_window(args):
    return screenshot.ScreenshotCapture().capture_window(args["title"], args.get("file", "window.png"))


def list_windows(args):
    return "\n".join(screenshot.ScreenshotCapture().list_windows())


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
    "show_virtual_cursor": show_virtual_cursor,
    "hide_virtual_cursor": hide_virtual_cursor,
}


class ReplyWorker(QThread):
    reply_ready = Signal(str, object, str)

    def __init__(self, agent, messages):
        super().__init__()
        self.agent = agent
        self.messages = messages

    def run(self):
        try:
            text, trace = self.agent.reply(self.messages)
            self.reply_ready.emit(text, trace, "")
        except Exception as error:
            self.reply_ready.emit("", [], str(error))
