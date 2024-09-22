import sys
from PyQt6.QtWidgets import (
    QApplication
)

from scr.mainWindow import *
      
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GameLauncher()
    ex.show()
    sys.exit(app.exec())
