import sys

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPolygon, QPen
from PySide6.QtWidgets import QApplication, QWidget

STEP = 8
FAST_STEP = 40
ARROW_COLOR = QColor("#e8a33d")
OUTLINE_COLOR = QColor("#1e1e1e")
TEXT_COLOR = QColor("#e0e0e0")


class VirtualCursor(QWidget):
    def __init__(self, keyboard_control=True):
        super().__init__()
        self.keyboard_control = keyboard_control
        self.position = [100, 100]
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

    def showEvent(self, event):
        super().showEvent(event)
        if self.keyboard_control:
            self.grabKeyboard()

    def show_cursor(self, x, y):
        self.move_to(x, y)
        self.show()
        self.raise_()

    def hide_cursor(self):
        self.hide()

    def keyPressEvent(self, event):
        step = FAST_STEP if event.modifiers() & Qt.ShiftModifier else STEP
        key = event.key()
        if key == Qt.Key_Up:
            self.move_to(self.position[0], self.position[1] - step)
        elif key == Qt.Key_Down:
            self.move_to(self.position[0], self.position[1] + step)
        elif key == Qt.Key_Left:
            self.move_to(self.position[0] - step, self.position[1])
        elif key == Qt.Key_Right:
            self.move_to(self.position[0] + step, self.position[1])
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            self.click_at(self.position[0], self.position[1])
        elif key == Qt.Key_Escape:
            self.quit()
        else:
            super().keyPressEvent(event)

    def move_to(self, x, y):
        screen = self.geometry()
        self.position = [
            max(screen.left() + 4, min(x, screen.right() - 4)),
            max(screen.top() + 4, min(y, screen.bottom() - 4)),
        ]
        self.update()

    def click_at(self, x, y):
        import pyautogui

        original = pyautogui.position()
        pyautogui.click(x, y)
        pyautogui.moveTo(original.x, original.y)

    def quit(self):
        self.releaseKeyboard()
        QApplication.instance().quit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        x, y = self.position
        points = QPolygon([
            QPoint(x, y),
            QPoint(x + 4, y + 20),
            QPoint(x + 8, y + 16),
            QPoint(x + 12, y + 24),
            QPoint(x + 17, y + 22),
            QPoint(x + 12, y + 13),
            QPoint(x + 18, y + 11),
        ])
        painter.setPen(QPen(OUTLINE_COLOR, 2))
        painter.setBrush(QBrush(ARROW_COLOR))
        painter.drawPolygon(points)

        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QPen(TEXT_COLOR))
        painter.drawText(x + 22, y + 10, f"{x}, {y}")
        painter.end()


def main():
    app = QApplication(sys.argv)
    cursor = VirtualCursor()
    cursor.show()
    print("Virtual cursor ready.")
    print("Arrow keys: move  |  Shift+Arrow: fast move  |  Enter: click  |  Esc: quit")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
