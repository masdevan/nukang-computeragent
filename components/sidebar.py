from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QButtonGroup, QFrame, QToolButton, QVBoxLayout
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SIDEBAR_WIDTH = 40
BUTTON_SIZE = 32
ICON_SIZE = 18
SPACING = 6


class Sidebar(QFrame):
    def __init__(self, icon_paths):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(SIDEBAR_WIDTH)
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(SPACING)
        for index, icon_path in enumerate(icon_paths):
            button = self.build_icon(icon_path)
            self.group.addButton(button, index)
            layout.addWidget(button)
        layout.addStretch()
        if self.group.buttons():
            self.group.buttons()[0].setChecked(True)

    def build_icon(self, icon_path):
        button = QToolButton()
        button.setObjectName("sideButton")
        button.setIcon(QIcon(str(PROJECT_ROOT / icon_path)))
        button.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
        button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        button.setCheckable(True)
        button.setCursor(Qt.PointingHandCursor)
        return button
