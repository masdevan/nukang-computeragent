from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget
from app.services.apps import cached_installed_apps, refresh_installed_apps
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

        apps_header = QHBoxLayout()
        apps_header.setSpacing(8)
        self.apps_section = QLabel("Installed Apps")
        self.apps_section.setObjectName("infoSection")
        apps_header.addWidget(self.apps_section)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("ghostButton")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.clicked.connect(self.refresh_apps)
        apps_header.addWidget(self.refresh_button)
        apps_header.addStretch(1)
        layout.addLayout(apps_header)

        self.apps_view = QTextEdit()
        self.apps_view.setObjectName("ocrViewer")
        self.apps_view.setReadOnly(True)
        layout.addWidget(self.apps_view, stretch=1)

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
        self.refresh_apps(force=False)

    def refresh_apps(self, force=True):
        apps = refresh_installed_apps() if force else cached_installed_apps()
        self.apps_section.setText(f"Installed Apps ({len(apps)})")
        self.apps_view.setPlainText("\n".join(apps))
