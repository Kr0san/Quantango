from PyQt6.QtWidgets import QDockWidget
from PyQt6.QtCore import Qt


class DockWidget(QDockWidget):
    """
    QDockwidget template to be used for individual dockable windows in the main window.
    """
    def __init__(self, name, widget, allowed_areas=Qt.DockWidgetArea.AllDockWidgetAreas,
                 features=None, delete_on_close=True, is_hidden=False):
        super().__init__()
        self.setWindowTitle(name)
        self.setWidget(widget)
        self.setObjectName(name)
        self.setAllowedAreas(allowed_areas)
        if features:
            self.setFeatures(features)
        if is_hidden:
            self.hide()
        if delete_on_close:
            self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
