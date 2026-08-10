from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QDialog, QLabel, QListWidget, QListWidgetItem, QMenu, QVBoxLayout, QWidget,
)
from components.confirm import ConfirmDialog
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CAPTURES_DIR = PROJECT_ROOT / "data" / "captures"
THUMB_SIZE = 110
VIEW_SIZE = 800


class GalleryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        self.image_list = QListWidget()
        self.image_list.setObjectName("galleryList")
        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setIconSize(QSize(THUMB_SIZE, THUMB_SIZE))
        self.image_list.setGridSize(QSize(THUMB_SIZE + 14, THUMB_SIZE + 34))
        self.image_list.setResizeMode(QListWidget.Adjust)
        self.image_list.setMovement(QListWidget.Static)
        self.image_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_list.customContextMenuRequested.connect(self.show_menu)
        self.image_list.itemDoubleClicked.connect(self.view_image)
        layout.addWidget(self.image_list)

        self.reload()

    def showEvent(self, event):
        super().showEvent(event)
        self.reload()

    def reload(self):
        self.image_list.clear()
        for path in sorted(CAPTURES_DIR.glob("*.png"), reverse=True):
            item = QListWidgetItem(QIcon(str(path)), path.stem)
            item.setData(Qt.UserRole, str(path))
            item.setToolTip(path.name)
            self.image_list.addItem(item)

    def show_menu(self, pos):
        item = self.image_list.itemAt(pos)
        if item is None:
            return
        menu = QMenu(self)
        view_action = menu.addAction("View")
        delete_action = menu.addAction("Delete")
        chosen = menu.exec(self.image_list.mapToGlobal(pos))
        if chosen == view_action:
            self.view_image(item)
        elif chosen == delete_action:
            self.confirm_delete(item)

    def view_image(self, item):
        pixmap = QPixmap(item.data(Qt.UserRole))
        if pixmap.isNull():
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(item.toolTip())
        layout = QVBoxLayout(dialog)
        label = QLabel()
        scaled = pixmap.scaled(VIEW_SIZE, VIEW_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaled)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        dialog.resize(min(scaled.width(), VIEW_SIZE) + 40, min(scaled.height(), VIEW_SIZE) + 60)
        dialog.exec()

    def confirm_delete(self, item):
        dialog = ConfirmDialog(self, "Delete this image?")
        if dialog.exec() == QDialog.Accepted:
            Path(item.data(Qt.UserRole)).unlink(missing_ok=True)
            self.reload()
