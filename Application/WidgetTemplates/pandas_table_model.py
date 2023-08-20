from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex, QVariant, pyqtSlot
import pandas as pd
from datetime import datetime
import numpy as np
import math


class PandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe """

    def __init__(self, data):
        super().__init__()
        self._data = data

    @property
    def dataframe(self):
        """
        Getter method. Returns dataframe from the current model.

        Returns
        -------
        `pd.Dataframe`
            Dataframe with the current data.
        """
        return self._data

    @dataframe.setter
    def dataframe(self, new_dataframe):
        """
        Setter method. Sets a new dataframe for the current model. Used to update positions table and import trade file.

        Parameters
        ----------
        new_dataframe : `pd.Dataframe`
            A new dataframe to be inserted.
        """
        self.beginResetModel()
        self._data = new_dataframe
        self.endResetModel()

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                value = self._data.iloc[index.row(), index.column()]

                if isinstance(value, datetime):
                    # Render time to YYYY-MM-DD.
                    return value.strftime("%Y-%m-%d")

                if isinstance(value, float):
                    # Render float to 2 dp and a thousand separator
                    return f'{value:,.2f}'

                if isinstance(value, (int, np.int64)):
                    # Render int with a thousand separator
                    return f'{value:,}'

                if value is None:
                    return ''

                return str(value)

    def rowCount(self, parent=QModelIndex()):
        return len(self._data.index)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data.columns)

    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled  # | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            self._data.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True

    @pyqtSlot(int, Qt.Orientation, result=str)
    def headerData(self, section: int, orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._data.columns[section]
            else:
                return str(self._data.index[section])
        return QVariant()

    def insertRows(self, position, rows, parent=QModelIndex(), new_data=None):
        """
        This method inserts a new row into the pandas dataframe model.

        Parameters
        ----------
        position : `int`
            Position to insert a new row.
        rows : `int`
            Number of rows to insert.
        parent : `QModelIndex`
            Selected index.
        new_data : `list`, optional
            New data to be inserted.
        """
        start, end = position, position + rows - 1
        if 0 <= start <= end:
            self.beginInsertRows(parent, start, end)
            for index in range(start, end + 1):
                if isinstance(new_data, list):
                    new_row = [[i] for i in new_data]
                else:
                    raise ValueError("Input must be a list")
                new_df = pd.DataFrame(dict(zip(list(self._data.columns), new_row)))
                self._data = pd.concat([self._data, new_df])
            self._data = self._data.reset_index(drop=True)
            self.endInsertRows()
            return True
        return False

    def removeRows(self, position, rows, parent=QModelIndex()):
        start, end = position, position + rows - 1
        if 0 <= start <= end < self.rowCount(parent):
            self.beginRemoveRows(parent, start, end)
            for index in range(start, end + 1):
                self._data.drop(index, inplace=True)
            self._data.reset_index(drop=True, inplace=True)
            self.endRemoveRows()
            return True
        return False

    def sort(self, ncol, order):
        """Sort table by given column number.
        """
        try:
            self.layoutAboutToBeChanged.emit()
            self._data.sort_values(self._data.columns[ncol], ascending=order == Qt.SortOrder.DescendingOrder,
                                   inplace=True)
            self._data.reset_index(drop=True, inplace=True)
            self.layoutChanged.emit()
        except Exception as e:
            print(e)
