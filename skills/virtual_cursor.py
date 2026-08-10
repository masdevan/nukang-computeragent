import sys
import time

from PySide6.QtCore import QPointF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QApplication, QWidget

STEP = 8
FAST_STEP = 40
MOVE_INTERVAL = 16
MOVE_MIN_MS = 60
MOVE_MAX_MS = 250
MOVE_MS_PER_PX = 0.4
ARROW_FILL = QColor("#ffffff")
ARROW_OUTLINE = QColor("#1e1e1e")

MAC_ARROW = [
    QPointF(0, 0),
    QPointF(3, 17),
    QPointF(6.5, 14.5),
    QPointF(8.5, 21),
    QPointF(11.5, 19.5),
    QPointF(9.5, 13),
    QPointF(14.5, 12),
]


class VirtualCursor(QWidget):
    def __init__(self, keyboard_control=True):
        super().__init__()
        self.keyboard_control = keyboard_control
        self.position = [100, 100]
        self.move_from = list(self.position)
        self.move_target = list(self.position)
        self.move_started = 0.0
        self.move_duration = 0
        self.move_timer = QTimer(self)
        self.move_timer.setInterval(MOVE_INTERVAL)
        self.move_timer.timeout.connect(self.move_step)
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
        target = [
            max(screen.left() + 4, min(x, screen.right() - 4)),
            max(screen.top() + 4, min(y, screen.bottom() - 4)),
        ]
        if target == self.move_target and self.move_timer.isActive():
            return
        self.move_from = list(self.position)
        self.move_target = target
        self.move_started = time.monotonic()
        distance = abs(target[0] - self.move_from[0]) + abs(target[1] - self.move_from[1])
        self.move_duration = max(MOVE_MIN_MS, min(MOVE_MAX_MS, distance * MOVE_MS_PER_PX)) / 1000
        self.move_timer.start()

    def move_step(self):
        progress = (time.monotonic() - self.move_started) / self.move_duration
        if progress >= 1:
            self.position = list(self.move_target)
            self.move_timer.stop()
        else:
            eased = 1 - (1 - progress) ** 3
            self.position = [
                round(self.move_from[0] + (self.move_target[0] - self.move_from[0]) * eased),
                round(self.move_from[1] + (self.move_target[1] - self.move_from[1]) * eased),
            ]
        self.update()

    def final_position(self):
        if self.move_timer.isActive():
            return list(self.move_target)
        return list(self.position)

    def move_by(self, dx, dy):
        self.move_to(self.position[0] + dx, self.position[1] + dy)

    def click_at(self, x, y, button="left"):
        from skills._mouse import click

        click(button, x, y)

    def double_click_at(self, x, y):
        from skills._mouse import click

        click("left", x, y, clicks=2, interval=0.05)

    def scroll_at(self, x, y, amount):
        from skills._mouse import scroll

        scroll(amount, x, y)

    def quit(self):
        self.releaseKeyboard()
        QApplication.instance().quit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        x, y = self.position
        points = QPolygonF([
            QPointF(x + point.x(), y + point.y()) for point in MAC_ARROW
        ])
        painter.setPen(QPen(ARROW_OUTLINE, 1))
        painter.setBrush(QBrush(ARROW_FILL))
        painter.drawPolygon(points)
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
