from PyQt6.QtWidgets import QToolBar, QTabWidget
from Application.Ribbon.ribbon_tab import RibbonTab
from Application.Ribbon import gui_scale
from Application.Ribbon.stylesheets import get_stylesheet


class RibbonWidget(QToolBar):
    def __init__(self, parent):
        QToolBar.__init__(self, parent)
        self.setStyleSheet(get_stylesheet("ribbon"))
        self.setObjectName("ribbonWidget")
        self.setWindowTitle("Ribbon")
        self._ribbon_widget = QTabWidget(self)
        self._ribbon_widget.setMaximumHeight(int(130*gui_scale()))
        self._ribbon_widget.setMinimumHeight(int(120*gui_scale()))
        self.setMovable(False)
        self.addWidget(self._ribbon_widget)

    def add_ribbon_tab(self, name):
        ribbon_tab = RibbonTab(self)
        ribbon_tab.setObjectName("tab_" + name)
        self._ribbon_widget.addTab(ribbon_tab, name)
        return ribbon_tab

    def set_active(self, name):
        self.setCurrentWidget(self.findChild("tab_" + name))
