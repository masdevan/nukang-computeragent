from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QVBoxLayout, QWidget,
)
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ConfirmDialog(QDialog):
    def __init__(self, parent, message):
        super().__init__(parent)
        self.setWindowTitle("Confirm")
        self.setModal(True)
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(QLabel(message))
        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Cancel")
        cancel.setObjectName("ghostButton")
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.clicked.connect(self.reject)
        buttons.addWidget(cancel)
        confirm = QPushButton("Delete")
        confirm.setObjectName("dangerButton")
        confirm.setCursor(Qt.PointingHandCursor)
        confirm.clicked.connect(self.accept)
        buttons.addWidget(confirm)
        layout.addLayout(buttons)


class SessionRow(QFrame):
    def __init__(self, name, created_at, on_delete, on_open):
        super().__init__()
        self.setObjectName("sessionRow")
        self.setCursor(Qt.PointingHandCursor)
        self.on_open = on_open

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 6, 0)
        layout.setSpacing(8)

        text_column = QVBoxLayout()
        text_column.setSpacing(3)
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.addStretch(1)
        name_label = QLabel(name)
        text_column.addWidget(name_label)
        time_label = QLabel(created_at.strftime("%d %b %Y, %H:%M"))
        time_label.setObjectName("sessionTime")
        text_column.addWidget(time_label)
        text_column.addStretch(1)
        layout.addLayout(text_column, stretch=1)

        delete_button = QPushButton()
        delete_button.setObjectName("deleteButton")
        delete_button.setIcon(QIcon(str(PROJECT_ROOT / "components" / "icons" / "trash.svg")))
        delete_button.setIconSize(QSize(15, 15))
        delete_button.setFixedSize(26, 26)
        delete_button.setCursor(Qt.PointingHandCursor)
        delete_button.clicked.connect(on_delete)
        layout.addWidget(delete_button)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_open()


class SessionPage(QWidget):
    def __init__(self, store, on_open):
        super().__init__()
        self.store = store
        self.on_open = on_open

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        self.session_list = QListWidget()
        self.session_list.setObjectName("sessionList")
        self.session_list.setSelectionMode(QListWidget.NoSelection)
        layout.addWidget(self.session_list)

        self.reload()

    def reload(self):
        self.session_list.clear()
        sessions = sorted(self.store.list_all(), key=lambda data: data["created_at"], reverse=True)
        for index, data in enumerate(sessions):
            self.add_session(data, index)

    def add_session(self, data, index):
        item = QListWidgetItem()
        created_at = datetime.fromisoformat(data["created_at"])
        row = SessionRow(
            f"Session {index + 1}",
            created_at,
            lambda: self.confirm_delete(data),
            lambda: self.on_open(data["id"]),
        )
        row.setFixedHeight(row.sizeHint().height())
        item.setSizeHint(QSize(0, row.height() + 12))
        self.session_list.addItem(item)
        self.session_list.setItemWidget(item, self.wrap_row(row))

    def wrap_row(self, row):
        wrapper = QWidget()
        wrapper.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(0)
        layout.addWidget(row)
        return wrapper

    def confirm_delete(self, data):
        dialog = ConfirmDialog(self, "Delete this session?")
        if dialog.exec() == QDialog.Accepted:
            self.store.delete(data["id"])
            self.reload()
