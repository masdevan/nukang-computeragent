from PySide6.QtCore import QThread, Signal

from app.services.tools import (
    MAX_STEPS, build_system_prompt, execute_tool, format_call,
    looks_like_tool_attempt, parse_tool_call,
)


class ReplyWorker(QThread):
    thinking_ready = Signal(str)
    chunk_ready = Signal(str)
    tool_ready = Signal(str)
    finished = Signal(str, str, str)

    def __init__(self, agent, messages, language):
        super().__init__()
        self.agent = agent
        self.messages = messages
        self.language = language
        self.stop_requested = False

    def request_stop(self):
        self.stop_requested = True

    def run(self):
        conversation = [{"role": "system", "content": build_system_prompt(self.language)}, *self.messages]
        try:
            client = self.agent.build_client()
        except Exception as error:
            self.finished.emit("", str(error), "error")
            return
        try:
            for _ in range(MAX_STEPS):
                if self.stop_requested:
                    self.finished.emit("", "", "stopped")
                    return
                stream = client.chat.completions.create(
                    model=self.agent.model, messages=conversation, stream=True
                )
                parts = []
                for chunk in stream:
                    if self.stop_requested:
                        break
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if delta is not None:
                        thinking = getattr(delta, "reasoning_content", None)
                        if thinking:
                            self.thinking_ready.emit(thinking)
                        content = delta.content
                        if content:
                            parts.append(content)
                            self.chunk_ready.emit(content)
                if self.stop_requested:
                    self.finished.emit("".join(parts), "", "stopped")
                    return
                text = "".join(parts)
                tool_call = parse_tool_call(text)
                if tool_call is None:
                    if looks_like_tool_attempt(text):
                        conversation.append({"role": "assistant", "content": text})
                        conversation.append({
                            "role": "user",
                            "content": (
                                "Your tool call JSON was malformed and could not be parsed. "
                                'Reply with ONLY a valid JSON object in this exact form: '
                                '{"tool": {"name": "<tool_name>", "args": {...}}} - '
                                "no other text, properly escaped quotes."
                            ),
                        })
                        continue
                    self.finished.emit(text, "", "done")
                    return
                self.tool_ready.emit(format_call(tool_call))
                result = execute_tool(tool_call)
                conversation.append({"role": "assistant", "content": text})
                conversation.append({"role": "user", "content": f"Tool result: {result}"})
            self.finished.emit("Task stopped after too many steps.", "", "done")
        except Exception as error:
            self.finished.emit("", str(error), "error")
