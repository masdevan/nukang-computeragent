from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QMouseEvent, QPixmap
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QVBoxLayout, QWidget,
)
from components.confirm import ConfirmDialog
from datetime import datetime
from pathlib import Path

from app.services.sessions import session_ranks
from pages.gallery_page import CAPTURES_DIR, show_capture_dialog

PROJECT_ROOT = Path(__file__).resolve().parents[1]
THUMB = 72


def session_captures(session_id):
    return sorted(CAPTURES_DIR.glob(f"{session_id}_*.png"))


def delete_session_artifacts(session_id):
    from skills.ocr import OCR_DIR

    for path in list(CAPTURES_DIR.glob(f"{session_id}_*.png")) + list(OCR_DIR.glob(f"{session_id}_*.txt")):
        path.unlink(missing_ok=True)


class CaptureThumb(QFrame):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.setFixedSize(THUMB, THUMB)
        self.setCursor(Qt.PointingHandCursor)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel()
        label.setPixmap(QPixmap(str(path)).scaled(THUMB, THUMB, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            show_capture_dialog(self, self.path)


class SessionRow(QFrame):
    def __init__(self, name, created_at, on_delete, on_open, captures):
        super().__init__()
        self.setObjectName("sessionRow")
        self.setCursor(Qt.PointingHandCursor)
        self.on_open = on_open

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 6, 0)
        layout.setSpacing(4)

        header = QHBoxLayout()
        header.setSpacing(8)
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
        header.addLayout(text_column, stretch=1)

        delete_button = QPushButton()
        delete_button.setObjectName("deleteButton")
        delete_button.setIcon(QIcon(str(PROJECT_ROOT / "components" / "icons" / "trash.svg")))
        delete_button.setIconSize(QSize(15, 15))
        delete_button.setFixedSize(26, 26)
        delete_button.setCursor(Qt.PointingHandCursor)
        delete_button.clicked.connect(on_delete)
        header.addWidget(delete_button)
        layout.addLayout(header)

        if captures:
            strip = QHBoxLayout()
            strip.setSpacing(6)
            for path in captures[-8:]:
                strip.addWidget(CaptureThumb(path))
            strip.addStretch(1)
            layout.addLayout(strip)

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

        self.new_session_button = QPushButton("New Session")
        self.new_session_button.setObjectName("ghostButton")
        self.new_session_button.setCursor(Qt.PointingHandCursor)
        self.new_session_button.clicked.connect(self.create_session)
        layout.addWidget(self.new_session_button, alignment=Qt.AlignLeft)

        self.session_list = QListWidget()
        self.session_list.setObjectName("sessionList")
        self.session_list.setSelectionMode(QListWidget.NoSelection)
        layout.addWidget(self.session_list)

        self.reload()

    def showEvent(self, event):
        super().showEvent(event)
        self.reload()

    def create_session(self):
        data = self.store.create()
        self.reload()
        self.on_open(data["id"])

    def reload(self):
        self.session_list.clear()
        sessions = self.store.list_all()
        ranks = session_ranks(sessions)
        for data in sorted(sessions, key=lambda item: item["created_at"], reverse=True):
            self.add_session(data, ranks[data["id"]])

    def add_session(self, data, rank):
        item = QListWidgetItem()
        created_at = datetime.fromisoformat(data["created_at"])
        row = SessionRow(
            f"Session {rank}",
            created_at,
            lambda: self.confirm_delete(data),
            lambda: self.on_open(data["id"]),
            session_captures(data["id"]),
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
        dialog = ConfirmDialog(self, "Delete this session and its images?")
        if dialog.exec() == QDialog.Accepted:
            delete_session_artifacts(data["id"])
            self.store.delete(data["id"])
            self.reload()
