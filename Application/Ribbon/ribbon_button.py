from PyQt6.QtCore import QSize, pyqtSlot, Qt
from PyQt6.QtWidgets import QToolButton, QPushButton

from Application.Ribbon import gui_scale
# from Application.Ribbon.stylesheets import get_stylesheet


class RibbonButton(QToolButton):
    def __init__(self, owner, action, is_large):
        QPushButton.__init__(self, owner)
        super().__init__()
        sc = gui_scale()
        self._actionOwner = action
        self.update_button_status_from_action()
        self.clicked.connect(self._actionOwner.trigger)
        self._actionOwner.changed.connect(self.update_button_status_from_action)

        if is_large:
            self.setMaximumWidth(int(120 * sc))
            self.setMinimumWidth(int(85 * sc))
            self.setMinimumHeight(int(85 * sc))
            self.setMaximumHeight(int(100 * sc))
            self.setToolButtonStyle(Qt.ToolButtonStyle(3))
            self.setIconSize(QSize(int(45 * sc), int(45 * sc)))
        else:
            self.setToolButtonStyle(Qt.ToolButtonStyle(2))
            self.setMaximumWidth(int(120 * sc))
            self.setIconSize(QSize(int(16 * sc), int(16 * sc)))

    @pyqtSlot()
    def update_button_status_from_action(self):
        self.setText(self._actionOwner.text())
        self.setStatusTip(self._actionOwner.statusTip())
        self.setToolTip(self._actionOwner.toolTip())
        self.setIcon(self._actionOwner.icon())
        self.setEnabled(self._actionOwner.isEnabled())
        self.setCheckable(self._actionOwner.isCheckable())
        self.setChecked(self._actionOwner.isChecked())
