from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

CREATOR_NAME = "Devan Yudistira Sugiharta"
PORTFOLIO_URL = "https://devansugiharta.my.id"


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
        portfolio.setObjectName("infoLink")
        portfolio.setTextFormat(Qt.RichText)
        portfolio.setOpenExternalLinks(True)
        portfolio.setCursor(Qt.PointingHandCursor)
        layout.addWidget(portfolio)

        layout.addStretch()
