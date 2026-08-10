from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QVBoxLayout, QWidget,
)
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = PROJECT_ROOT / "skills"

SKILL_DESCRIPTIONS = {
    "virtual_cursor": "Second cursor, keyboard-controlled",
    "keyboard_controls": "Press key combos and type text",
    "mouse_control": "Move, click, scroll, back/forward",
    "screenshot": "Capture screen or a specific window",
    "app_launcher": "Launch apps and run commands",
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
            self.add_skill(path.stem)

    def add_skill(self, name):
        item = QListWidgetItem()
        row = SkillRow(name, SKILL_DESCRIPTIONS.get(name, "Skill"))
        row.setFixedHeight(row.sizeHint().height())
        item.setSizeHint(QSize(0, row.height() + 8))
        self.skill_list.addItem(item)
        self.skill_list.setItemWidget(item, row)
