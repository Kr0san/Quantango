from PyQt6 import QtCore
from PyQt6.QtCore import Qt


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data=[[]], header_data=[], header_position=QtCore.Qt.Horizontal):
        super(TableModel, self).__init__()
        self._data = data
        self._header_data = header_data

        row_counter = 0
        for row_item in self._data:
            column_counter = 0
            for column_item in row_item:
                idx = self.createIndex(row_counter, column_counter)
                self.setData(idx, column_item, Qt.EditRole)
                self.dataChanged.emit(idx, idx)
                column_counter += 1
            row_counter += 1

        num_headers = len(self._header_data)
        for section in range(0, num_headers):
            self.setHeaderData(section, header_position, self._header_data[section])
        self.headerDataChanged.emit(header_position, 0, num_headers)

    def index(self, row, column, parent):
        if row < 0 or row >= len(self._data):
            return QtCore.QModelIndex()
        return self.createIndex(row, column, self._data[row])

    def data(self, index, role):
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            if row < 0 or row >= len(self._data):
                return ""
            if column < 0 or column >= len(self._data[row]):
                return ""
            else:
                return self._data[row][column]
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid:
            return False
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            if row < 0 or row >= self.rowCount(QtCore.QModelIndex()):
                return False
            if column < 0 or column >= len(self._data[row]):
                return False
            self._data[row].pop(column)
            self._data[row].insert(column, value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def rowCount(self, index):
        if index.isValid():
            return

        num_rows = len(self._data)

        # checking for empty nested columns list within a single "row"
        if num_rows == 1:
            if len(self._data[0]) == 0:
                return 0

        return num_rows

    def columnCount(self, index):
        if index.isValid():
            return 0

        # compute the max column count within all rows
        max_column_count = 0
        for row in self._data:
            column_count = len(row)
            if column_count > max_column_count:
                max_column_count = column_count

        # if there are no real columns, make the column count return the number of headers instead
        if max_column_count < len(self._header_data):
            max_column_count = len(self._header_data)
        return max_column_count

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section < 0 or section >= len(self._header_data):
                    return ""
                else:
                    return self._header_data[section]
            if orientation == Qt.Vertical:
                if section < 0 or section >= len(self._header_data):
                    return ""
                else:
                    return self._header_data[section]
        return None

    def insertRows(self, row, count, index):
        if index.isValid():
            return False
        if count <= 0:
            return False
        num_columns = self.columnCount(index)
        # inserting 'count' empty rows starting at 'row'
        self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)
        for i in range(0, count):
            # inserting as many columns as the table currently has
            self._data.insert(row + i, ["" for i in range(0, num_columns)])
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, index):
        self.beginRemoveRows(index, position, position+rows-1)
        for i in range(rows):
            del(self._data[position])
        self.endRemoveRows()
        self.layoutChanged.emit()
        return True
