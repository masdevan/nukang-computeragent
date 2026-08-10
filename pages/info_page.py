from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from app.services.device import collect_device_info

CREATOR_NAME = "Devan Yudistira Sugiharta"
PORTFOLIO_URL = "https://devansugiharta.my.id"

DEVICE_ROWS = [
    ("OS", "os"),
    ("Screen", "screen"),
    ("CPU", "cpu"),
    ("RAM", "ram_gb"),
]


class InfoPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        made_by = QLabel("Made by")
        made_by.setObjectName("infoMuted")
        layout.addWidget(made_by)

        creator = QLabel(CREATOR_NAME)
        creator.setObjectName("infoCreator")
        layout.addWidget(creator)

        portfolio = QLabel(f'<a href="{PORTFOLIO_URL}" style="color: #7eb8ff;">{PORTFOLIO_URL}</a>')
        portfolio.setTextFormat(Qt.RichText)
        portfolio.setOpenExternalLinks(True)
        portfolio.setCursor(Qt.PointingHandCursor)
        layout.addWidget(portfolio)

        self.device_section = QLabel("Your Device")
        self.device_section.setObjectName("infoSection")
        layout.addWidget(self.device_section)

        self.device_rows = {}
        for key, _ in DEVICE_ROWS:
            row = QLabel()
            row.setTextFormat(Qt.RichText)
            layout.addWidget(row)
            self.device_rows[key] = row

        layout.addStretch()

    def showEvent(self, event):
        super().showEvent(event)
        info = collect_device_info()
        for key, field in DEVICE_ROWS:
            value = info.get(field, "unknown")
            if field == "ram_gb":
                value = f"{value} GB"
            safe = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            safe = safe.replace("\n", "<br/>")
            self.device_rows[key].setText(
                f'<span style="color: #8a8a8a;">{key}:</span> '
                f'<span style="color: #e0e0e0;">{safe}</span>'
            )
