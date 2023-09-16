import sys
from PyQt6.QtWidgets import QApplication
from Application.main_window import MainWindow
import qdarktheme

"""
This is the main file of the application. It is responsible for starting the application and loading the main window.
QuanTango is a personal project by me, and is not intended for commercial use. 
"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarktheme.load_stylesheet())
    app.setQuitOnLastWindowClosed(True)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
