import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from views.main_window import MainWindow


def main():
    """Main entry point for the application."""
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
