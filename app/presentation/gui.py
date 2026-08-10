from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QHBoxLayout, QStackedWidget, QWidget
from app.services.config import DEFAULT_BASE_URL, DEFAULT_MODEL, load_config
from app.services.llm import ToolAgent, ReplyWorker
from app.services.sessions import SessionStore
from components.sidebar import Sidebar
from pages.chat_page import ChatPage
from pages.gallery_page import GalleryPage
from pages.session_page import SessionPage
from pages.settings_page import SettingsPage
from pages.skills_page import SkillsPage

DARK_STYLE = """
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Segoe UI";
    font-size: 10pt;
}
QLabel { background: transparent; }
QFrame#sidebar { background-color: #252526; }
QStackedWidget { background-color: #252526; }
QToolButton#sideButton { background: transparent; border: none; border-radius: 6px; }
QToolButton#sideButton:hover { background: #2d2d30; }
QToolButton#sideButton:checked { background: #37373d; }
QFrame#inputContainer {
    background-color: #1e1e1e;
    border: 1px solid #333333;
    border-radius: 0;
}
QTextEdit#messageInput { background: transparent; border: none; }
QPushButton#sendButton {
    background-color: #3a3a3a;
    border: none;
    border-radius: 15px;
}
QPushButton#sendButton:hover { background-color: #454545; }
QPushButton#sendButton:pressed { background-color: #2e2e2e; }
QPushButton#ghostButton {
    background-color: #252526;
    color: #e0e0e0;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    padding: 4px 12px;
}
QPushButton#ghostButton:hover { background-color: #2d2d30; }
QPushButton#dangerButton {
    background-color: #8a1f1f;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 4px 12px;
}
QPushButton#dangerButton:hover { background-color: #a12d2d; }
QListWidget#sessionList { background: transparent; border: none; outline: none; }
QListWidget#sessionList::item { background: transparent; border: none; }
QListWidget#galleryList { background: transparent; border: none; outline: none; }
QListWidget#galleryList::item { border-radius: 4px; color: #9d9d9d; }
QListWidget#galleryList::item:hover { background: #2d2d30; }
QListWidget#galleryList::item:selected { background: #37373d; }
QMenu {
    background-color: #252526;
    color: #e0e0e0;
    border: 1px solid #3a3a3a;
}
QMenu::item { padding: 4px 24px; }
QMenu::item:selected { background-color: #0e639c; }
QFrame#sessionRow { background: #1e1e1e; border-radius: 6px; }
QLabel#sessionTime { color: #8a8a8a; font-size: 7pt; }
QPushButton#deleteButton {
    background: transparent;
    border: none;
    border-radius: 6px;
}
QPushButton#deleteButton:hover { background: #454545; }
QLineEdit#settingsInput {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    padding: 6px 8px;
    selection-background-color: #264f78;
}
QLineEdit#settingsInput:focus { border-color: #0e639c; }
QWidget#keyContainer {
    background-color: #1e1e1e;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
}
QLineEdit#keyInput {
    background: transparent;
    color: #e0e0e0;
    border: none;
    selection-background-color: #264f78;
}
QToolButton#eyeButton { background: transparent; border: none; border-radius: 4px; }
QToolButton#eyeButton:hover { background: #2d2d30; }
QFrame#skillRow { background: #1e1e1e; border-radius: 6px; }
QLabel#skillName { color: #e0e0e0; font-weight: bold; }
QLabel#skillDescription { color: #8a8a8a; font-size: 8pt; }
QPushButton#saveButton {
    background-color: #0e639c;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 20px;
}
QPushButton#saveButton:hover { background-color: #1177bb; }
QLabel#statusLabel { color: #6a9955; }
QScrollBar:vertical { background: #252526; width: 12px; }
QScrollBar::handle:vertical { background: #3a3a3a; border-radius: 6px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: #252526; }
"""


def apply_pure_dark(qapp):
    qapp.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#1e1e1e"))
    palette.setColor(QPalette.WindowText, QColor("#e0e0e0"))
    palette.setColor(QPalette.Base, QColor("#252526"))
    palette.setColor(QPalette.AlternateBase, QColor("#252526"))
    palette.setColor(QPalette.Text, QColor("#e0e0e0"))
    palette.setColor(QPalette.Button, QColor("#0e639c"))
    palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
    palette.setColor(QPalette.Highlight, QColor("#264f78"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.Disabled, QPalette.Button, QColor("#3a3a3a"))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#9d9d9d"))
    qapp.setPalette(palette)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.store = SessionStore()
        self.current_session = None
        self.reply_worker = None

        self.setWindowTitle("Nukang Computer Agent")
        self.resize(640, 480)
        self.setStyleSheet(DARK_STYLE)
        try:
            self.setWindowFlag(Qt.WindowDarkMode)
        except AttributeError:
            pass

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.pages = QStackedWidget()
        self.chat_page = ChatPage(self.handle_message)
        self.session_page = SessionPage(self.store, self.open_session)
        self.gallery_page = GalleryPage()
        self.pages.addWidget(self.chat_page)
        self.pages.addWidget(self.session_page)
        self.pages.addWidget(SkillsPage())
        self.pages.addWidget(self.gallery_page)
        self.pages.addWidget(SettingsPage())

        self.sidebar = Sidebar([
            "components/icons/chat.svg",
            "components/icons/session.svg",
            "components/icons/skills.svg",
            "components/icons/image.svg",
            "components/icons/settings.svg",
        ])
        self.sidebar.group.idClicked.connect(self.pages.setCurrentIndex)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.divider_strip())
        layout.addWidget(self.pages, stretch=1)

    def handle_message(self, message):
        if self.current_session is None:
            self.current_session = self.store.create()
            self.session_page.reload()
        data = self.store.load(self.current_session["id"])
        data["messages"].append({"role": "user", "content": message})
        self.store.save(data)
        config = load_config()
        agent = ToolAgent(
            config.get("base_url", DEFAULT_BASE_URL),
            config.get("api_key", ""),
            config.get("model", DEFAULT_MODEL),
        )
        self.reply_worker = ReplyWorker(agent, data["messages"])
        self.reply_worker.reply_ready.connect(self.handle_reply)
        self.reply_worker.start()

    def handle_reply(self, reply, trace, error):
        if error:
            self.chat_page.append_agent(f"Error: {error}")
            return
        for step in trace:
            self.chat_page.append_agent(f"[tool] {step}")
        data = self.store.load(self.current_session["id"])
        data["messages"].append({"role": "assistant", "content": reply})
        self.store.save(data)
        self.chat_page.append_agent(reply)

    def open_session(self, session_id):
        data = self.store.load(session_id)
        self.current_session = data
        self.chat_page.load_conversation(data["messages"])
        self.pages.setCurrentIndex(0)

    def divider_strip(self):
        strip = QWidget()
        strip.setFixedWidth(8)
        return strip
