import sys
from PySide6.QtWidgets import QApplication
from app.presentation.gui import App, apply_pure_dark


def main():
    qapp = QApplication(sys.argv)
    apply_pure_dark(qapp)
    app = App()
    app.show()
    sys.exit(qapp.exec())


if __name__ == "__main__":
    main()
