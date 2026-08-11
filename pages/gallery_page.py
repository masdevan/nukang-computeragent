from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMenu,
    QPushButton, QTextEdit, QVBoxLayout, QWidget,
)
from components.confirm import ConfirmDialog
from skills.general.ocr import OCR_DIR
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CAPTURES_DIR = PROJECT_ROOT / "data" / "captures"
THUMB_SIZE = 110
VIEW_SIZE = 800


def thumbnail(path, size=THUMB_SIZE):
    pixmap = QPixmap(path)
    if pixmap.isNull():
        return QIcon()
    pixmap = pixmap.scaled(
        size, size,
        Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation,
    )
    left = (pixmap.width() - size) // 2
    top = (pixmap.height() - size) // 2
    pixmap = pixmap.copy(left, top, size, size)
    return QIcon(pixmap)


def show_capture_dialog(parent, path, title=None):
    path = Path(path)
    pixmap = QPixmap(str(path))
    if pixmap.isNull():
        return
    dialog = QDialog(parent)
    dialog.setWindowTitle(title or path.name)
    dialog.resize(900, 560)
    layout = QHBoxLayout(dialog)
    layout.setSpacing(8)

    image_label = QLabel()
    scaled = pixmap.scaled(560, 520, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    image_label.setPixmap(scaled)
    image_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(image_label, stretch=1)

    ocr_text = QTextEdit()
    ocr_text.setObjectName("ocrViewer")
    ocr_text.setReadOnly(True)
    sidecar = OCR_DIR / f"{path.stem}.txt"
    if sidecar.exists():
        ocr_text.setPlainText(sidecar.read_text(encoding="utf-8"))
    else:
        ocr_text.setPlainText("(no OCR text)")
    layout.addWidget(ocr_text, stretch=1)

    dialog.exec()


class GalleryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_selected)
        layout.addWidget(self.delete_button, alignment=Qt.AlignLeft)

        self.image_list = QListWidget()
        self.image_list.setObjectName("galleryList")
        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setIconSize(QSize(THUMB_SIZE, THUMB_SIZE))
        self.image_list.setGridSize(QSize(THUMB_SIZE + 14, THUMB_SIZE + 34))
        self.image_list.setResizeMode(QListWidget.Adjust)
        self.image_list.setMovement(QListWidget.Static)
        self.image_list.setUniformItemSizes(True)
        self.image_list.setWordWrap(True)
        self.image_list.setTextElideMode(Qt.ElideMiddle)
        self.image_list.setSelectionMode(QListWidget.SingleSelection)
        self.image_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_list.customContextMenuRequested.connect(self.show_menu)
        self.image_list.itemDoubleClicked.connect(self.view_image)
        self.image_list.itemSelectionChanged.connect(self.update_delete_state)
        layout.addWidget(self.image_list)

        self.reload()

    def showEvent(self, event):
        super().showEvent(event)
        self.reload()

    def reload(self):
        self.image_list.clear()
        for path in sorted(CAPTURES_DIR.glob("*.png"), reverse=True):
            item = QListWidgetItem(thumbnail(str(path)), path.stem)
            item.setData(Qt.UserRole, str(path))
            item.setToolTip(path.name)
            self.image_list.addItem(item)
        self.update_delete_state()

    def update_delete_state(self):
        self.delete_button.setEnabled(self.image_list.currentItem() is not None)

    def delete_selected(self):
        item = self.image_list.currentItem()
        if item is not None:
            self.confirm_delete(item)

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
        show_capture_dialog(self, item.data(Qt.UserRole), item.toolTip())

    def confirm_delete(self, item):
        dialog = ConfirmDialog(self, "Delete this image?")
        if dialog.exec() == QDialog.Accepted:
            path = Path(item.data(Qt.UserRole))
            path.unlink(missing_ok=True)
            (OCR_DIR / f"{path.stem}.txt").unlink(missing_ok=True)
            self.reload()
