from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QToolButton, QVBoxLayout, QWidget,
)
from app.services.config import (
    DEFAULT_BASE_URL, DEFAULT_MODEL, load_config, save_config,
)
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_HEIGHT = 36


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        current = load_config()
        self.url_input = QLineEdit(current.get("base_url", DEFAULT_BASE_URL))
        self.url_input.setObjectName("settingsInput")
        self.url_input.setFixedHeight(INPUT_HEIGHT)
        self.url_input.setPlaceholderText(DEFAULT_BASE_URL)
        form.addRow("Base URL", self.url_input)

        self.key_input = QLineEdit(current.get("api_key", ""))
        self.key_input.setObjectName("keyInput")
        self.key_input.setFixedHeight(INPUT_HEIGHT)
        self.key_input.setPlaceholderText("sk-...")
        self.key_input.setEchoMode(QLineEdit.Password)

        key_container = QWidget()
        key_container.setObjectName("keyContainer")
        key_container.setFixedHeight(INPUT_HEIGHT)
        key_layout = QHBoxLayout(key_container)
        key_layout.setContentsMargins(8, 2, 4, 2)
        key_layout.setSpacing(4)
        key_layout.addWidget(self.key_input)
        self.eye_icon = QIcon(str(PROJECT_ROOT / "components" / "icons" / "eye.svg"))
        self.eye_off_icon = QIcon(str(PROJECT_ROOT / "components" / "icons" / "eye_off.svg"))
        self.eye_button = QToolButton()
        self.eye_button.setObjectName("eyeButton")
        self.eye_button.setIcon(self.eye_icon)
        self.eye_button.setIconSize(QSize(16, 16))
        self.eye_button.setFixedSize(26, 26)
        self.eye_button.setCursor(Qt.PointingHandCursor)
        self.eye_button.clicked.connect(self.toggle_key_visibility)
        key_layout.addWidget(self.eye_button)

        form.addRow("API Key", key_container)

        self.model_input = QLineEdit(current.get("model", DEFAULT_MODEL))
        self.model_input.setObjectName("settingsInput")
        self.model_input.setFixedHeight(INPUT_HEIGHT)
        self.model_input.setPlaceholderText(DEFAULT_MODEL)
        form.addRow("Model", self.model_input)

        layout.addLayout(form)

        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("saveButton")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self.save)
        layout.addWidget(self.save_button, alignment=Qt.AlignLeft)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)

        layout.addStretch()

    def toggle_key_visibility(self):
        visible = self.key_input.echoMode() == QLineEdit.Normal
        self.key_input.setEchoMode(QLineEdit.Password if visible else QLineEdit.Normal)
        self.eye_button.setIcon(self.eye_off_icon if visible else self.eye_icon)

    def save(self):
        save_config({
            "base_url": self.url_input.text().strip(),
            "api_key": self.key_input.text().strip(),
            "model": self.model_input.text().strip(),
        })
        self.status_label.setText("Saved.")
