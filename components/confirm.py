from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


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
