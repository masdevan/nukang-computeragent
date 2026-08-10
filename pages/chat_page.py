from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QKeyEvent
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QTextEdit, QVBoxLayout, QWidget
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class MessageInput(QTextEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
            self.send_callback()
        else:
            super().keyPressEvent(event)


class ChatPage(QWidget):
    def __init__(self, on_send):
        super().__init__()
        self.on_send = on_send

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Start a conversation...")
        layout.addWidget(self.chat_history, stretch=1)

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

        self.send_button = QPushButton()
        self.send_button.setObjectName("sendButton")
        self.send_button.setIcon(QIcon(str(PROJECT_ROOT / "components" / "icons" / "send.svg")))
        self.send_button.setIconSize(QSize(14, 14))
        self.send_button.setFixedSize(30, 30)
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.clicked.connect(self.send)
        input_row.addWidget(self.send_button, alignment=Qt.AlignBottom)
        layout.addWidget(input_container)

    def send(self):
        message = self.message_input.toPlainText().strip()
        if not message:
            return
        self.append_user(message)
        self.message_input.clear()
        self.on_send(message)

    def append_user(self, message):
        self.chat_history.append(f"You: {message}")
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())

    def append_agent(self, message):
        self.chat_history.append(f"Agent: {message}")
        self.chat_history.verticalScrollBar().setValue(self.chat_history.verticalScrollBar().maximum())

    def load_conversation(self, messages):
        self.chat_history.clear()
        for message in messages:
            if message["role"] == "user":
                self.append_user(message["content"])
            else:
                self.append_agent(message["content"])
