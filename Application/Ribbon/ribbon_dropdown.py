from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import pyqtSlot


class RibbonDropdown(QComboBox):
    """
    This class defines combo box used in the application ribbon.

    Parameters
    ----------
    items : `list`
        List of items to be added to the combo box.
    min_width : `int`, optional
        Minimum width of the widget.
    """
    def __init__(self, items, min_width=50, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(min_width)
        self.addItems(items)

    @pyqtSlot(str)
    def delete_item(self, name):
        """
        Convenience function to delete combo box items using name.

        Parameters
        ----------
        name : `str`
            Name of the item to be deleted.
        """
        index = self.findText(name)
        self.removeItem(index)
