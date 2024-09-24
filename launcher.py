import sys
from PyQt6.QtWidgets import (
    QApplication
)

from PyQt6.QtGui import QIcon

from scr.mainWindow import *

def apply_dark_theme(app):
    dark_style = """
    QWidget {
        background-color: #2E2E2E;
        color: #FFFFFF;
    }
    QMainWindow {
        background-color: #2E2E2E;
        color: #FFFFFF;
    }
    QWindow {
        background-color: #2E2E2E;
        color: #FFFFFF;
    }
    QStatusBar {
        background-color: #333333;
        color: #FFFFFF;
    }
    QPushButton {
        background-color: #444444;
        color: #FFFFFF;
    }
    QPushButton:hover {
        background-color: #555555;
    }
    QLineEdit {
        background-color: #333333;
        color: #FFFFFF;
    }
    """
    app.setStyleSheet(dark_style)
    app.setWindowIcon(QIcon("../scr/icon.ico"))

      
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GameLauncher()
    apply_dark_theme(app)
    ex.show()
    sys.exit(app.exec())


