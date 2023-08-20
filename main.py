import sys
from PyQt6.QtWidgets import QApplication
from Application.main_window import MainWindow
import qdarktheme
# from qt_material import apply_stylesheet

__author__ = 'iSsential'

# extra = {
#     'font_family': 'calibri',
#     'density_scale': '-2',
# }


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # qdarktheme.setup_theme()
    app.setStyleSheet(qdarktheme.load_stylesheet())
    app.setQuitOnLastWindowClosed(True)
    # apply_stylesheet(app, theme='light_amber.xml', extra=extra)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

