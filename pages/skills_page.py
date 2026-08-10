from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QVBoxLayout, QWidget,
)
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = PROJECT_ROOT / "skills"

SKILL_DESCRIPTIONS = {
    "keyboard_controls": "Press key combos and type text",
    "left_click": "Left click with mouse",
    "right_click": "Right click with mouse",
    "double_click": "Double click with mouse",
    "hold_left_click": "Hold left mouse button",
    "scroll_down": "Scroll the mouse wheel down",
    "scroll_up": "Scroll the mouse wheel up",
    "back": "Press the mouse back button",
    "forward": "Press the mouse forward button",
    "screenshot": "Capture screen or a specific window",
    "app_launcher": "Launch apps and run commands",
    "window_focus": "Focus a window by title",
    "close_app": "Close a window gracefully by title",
    "file_ops": "Read files from disk",
    "ocr": "Extract text with coordinates from screenshots",
}


class SkillRow(QFrame):
    def __init__(self, name, description):
        super().__init__()
        self.setObjectName("skillRow")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(8)
        name_label = QLabel(name)
        name_label.setObjectName("skillName")
        layout.addWidget(name_label)
        layout.addStretch()
        description_label = QLabel(description)
        description_label.setObjectName("skillDescription")
        layout.addWidget(description_label)


class SkillsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        self.skill_list = QListWidget()
        self.skill_list.setObjectName("sessionList")
        self.skill_list.setSelectionMode(QListWidget.NoSelection)
        layout.addWidget(self.skill_list)

        for path in sorted(SKILLS_DIR.glob("*.py")):
            if path.stem.startswith("_"):
                continue
            self.add_skill(path.stem)

    def add_skill(self, name):
        item = QListWidgetItem()
        row = SkillRow(name, SKILL_DESCRIPTIONS.get(name, "Skill"))
        row.setFixedHeight(row.sizeHint().height())
        item.setSizeHint(QSize(0, row.height() + 8))
        self.skill_list.addItem(item)
        self.skill_list.setItemWidget(item, row)
