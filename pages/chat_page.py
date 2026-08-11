from PySide6.QtCore import QRect, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QIcon, QKeyEvent, QPainter, QPen, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget,
)
import html
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
USER_COLOR = QColor("#7eb8ff")
AGENT_COLOR = QColor("#e0e0e0")
TOOL_COLOR = QColor("#8a8a8a")
THINKING_COLOR = QColor("#5f6b7a")


class Spinner(QWidget):
    def __init__(self, size=14):
        super().__init__()
        self.angle = 0
        self.setFixedSize(size, size)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(80)

    def rotate(self):
        self.angle = (self.angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor("#0e639c"), 2)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        margin = 2
        painter.drawArc(QRect(margin, margin, self.width() - 2 * margin, self.height() - 2 * margin), self.angle * 16, 270 * 16)
        painter.end()


class MessageInput(QTextEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
            self.send_callback()
        else:
            super().keyPressEvent(event)


class ChatPage(QWidget):
    def __init__(self, on_send, on_stop):
        super().__init__()
        self.on_send = on_send
        self.on_stop = on_stop
        self.streaming = False
        self.thinking_anchor = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Start a conversation...")
        layout.addWidget(self.chat_history, stretch=1)

        self.thinking_row = QWidget()
        thinking_layout = QHBoxLayout(self.thinking_row)
        thinking_layout.setContentsMargins(2, 0, 0, 0)
        thinking_layout.setSpacing(6)
        thinking_layout.addWidget(Spinner())
        thinking_label = QLabel("Thinking...")
        thinking_label.setObjectName("thinkingLabel")
        thinking_layout.addWidget(thinking_label)
        thinking_layout.addStretch()
        self.thinking_row.hide()
        layout.addWidget(self.thinking_row)

        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        input_container.setFixedHeight(52)
        input_row = QHBoxLayout(input_container)
        input_row.setContentsMargins(12, 8, 8, 8)
        input_row.setSpacing(8)
        self.message_input = MessageInput()
        self.message_input.setObjectName("messageInput")
        self.message_input.setPlaceholderText("Message the agent...")
        self.message_input.send_callback = self.send
        input_row.addWidget(self.message_input, stretch=1)

        self.send_icon = QIcon(str(PROJECT_ROOT / "components" / "icons" / "send.svg"))
        self.stop_icon = QIcon(str(PROJECT_ROOT / "components" / "icons" / "stop.svg"))
        self.send_button = QPushButton()
        self.send_button.setObjectName("sendButton")
        self.send_button.setIcon(self.send_icon)
        self.send_button.setIconSize(QSize(14, 14))
        self.send_button.setFixedSize(30, 30)
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.clicked.connect(self.button_clicked)
        input_row.addWidget(self.send_button, alignment=Qt.AlignBottom)
        layout.addWidget(input_container)

    def button_clicked(self):
        if self.streaming:
            self.on_stop()
        else:
            self.send()

    def send(self):
        message = self.message_input.toPlainText().strip()
        if not message:
            return
        self.append_user(message)
        self.message_input.clear()
        self.on_send(message)

    def start_stream(self):
        self.thinking_anchor = None
        self.set_streaming(True)
        self.thinking_row.show()

    def set_streaming(self, streaming):
        self.streaming = streaming
        self.send_button.setIcon(self.stop_icon if streaming else self.send_icon)
        self.message_input.setEnabled(not streaming)

    def stream_thinking(self, chunk):
        if self.thinking_anchor is None:
            self.thinking_anchor = self.chat_history.textCursor().position()
            self.insert_colored("Thinking: ", THINKING_COLOR)
        self.insert_colored(chunk, THINKING_COLOR)

    def stream_chunk(self, chunk):
        if self.thinking_anchor is None:
            self.thinking_anchor = self.chat_history.textCursor().position()
            self.insert_colored("Thinking: ", THINKING_COLOR)
        self.insert_colored(chunk, THINKING_COLOR)

    def clear_thinking(self):
        if self.thinking_anchor is None:
            return
        cursor = self.chat_history.textCursor()
        cursor.setPosition(self.thinking_anchor)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        self.thinking_anchor = None

    def stream_tool(self, line):
        self.clear_thinking()
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_history.setTextCursor(cursor)
        box = (
            '<div style="background-color:#252526; border:1px solid #3a3a3a; '
            'border-radius:6px; padding:4px 10px; color:#8a8a8a; margin:2px 0;">'
            f"{html.escape(line)}</div><br/>"
        )
        cursor.insertHtml(box)
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())

    def stream_finish(self, text, error, status):
        self.set_streaming(False)
        self.thinking_row.hide()
        self.clear_thinking()
        if error:
            self.append_colored(f"Error: {error}", TOOL_COLOR)
            return ""
        if status == "stopped":
            if text:
                self.append_colored(f"Agent: {text}", AGENT_COLOR)
                return text
            self.append_colored("(stopped)", TOOL_COLOR)
            return "(stopped)"
        self.append_colored(f"Agent: {text}", AGENT_COLOR)
        return text

    def append_user(self, message):
        self.append_colored(f"You: {message}", USER_COLOR)

    def append_agent(self, message):
        self.append_colored(f"Agent: {message}", AGENT_COLOR)

    def append_colored(self, text, color):
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_history.setTextCursor(cursor)
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        cursor.insertText(text + "\n", fmt)
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())

    def insert_colored(self, text, color):
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_history.setTextCursor(cursor)
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        cursor.insertText(text, fmt)
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())

    def load_conversation(self, messages):
        self.chat_history.clear()
        for message in messages:
            if message["role"] == "user":
                self.append_user(message["content"])
            else:
                self.append_agent(message["content"])
