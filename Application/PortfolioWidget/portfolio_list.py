from PyQt6.QtWidgets import QTreeView, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QStandardItemModel, QStandardItem


class StandardItem(QStandardItem):
    """
    This class is used to define a row item (ptf) for a QTreeView object.

    Parameters
    ----------
    name : `str`
        Label of the ptf.
    cash : `float`
        Starting balance of the ptf.
    date : `str`
        Starting date of the ptf.
    curr : `str`
        Starting currency of the ptf.
    font_size : `int`, optional
        Font size of the label.
    set_bold : `bool`, optional
        Sets label text to bold if set to True.
    """
    def __init__(self, name='', cash=0.0, date='', curr='USD', font_size=10, set_bold=False):
        super().__init__()
        fnt = QFont('Calibri', font_size)
        fnt.setBold(set_bold)
        self.setEditable(False)
        self.setFont(fnt)
        self.setText(name)
        self.setData(name, Qt.ItemDataRole.UserRole)
        self.setData(cash, Qt.ItemDataRole.UserRole+1)
        self.setData(date, Qt.ItemDataRole.UserRole+2)
        self.setData(curr, Qt.ItemDataRole.UserRole+3)


class PortfolioList(QTreeView):
    """
    This class defines portfolio list widget using QTreeView object.
    """
    def __init__(self):
        QTreeView.__init__(self, None)
        self.setHeaderHidden(True)
        self.treeModel = QStandardItemModel()
        self.rootNode = self.treeModel.invisibleRootItem()

        self.portfolio_list = StandardItem('Portfolio List', set_bold=True)
        portfolio_one = StandardItem('Main Portfolio', cash=100000.0, date='2022-01-01', curr='USD')

        self.portfolio_list.appendRow(portfolio_one)
        self.rootNode.appendRow(self.portfolio_list)
        self.setModel(self.treeModel)
        self.expandAll()

        self._deleted_ptf = ''  # This holds the name of the deleted portfolio
        # self.doubleClicked.connect(self.get_value)

    @property
    def deleted_ptf(self):
        """
        Getter method of self._deleted_ptf.

        Returns
        -------
        `str`
            Deleted ptf name.
        """
        return self._deleted_ptf

    @deleted_ptf.setter
    def deleted_ptf(self, deleted_ptf_name):
        """
        Setter method of self._deleted_ptf.

        Parameters
        ----------
        deleted_ptf_name : `str`
            New deleted portfolio.
        """
        self._deleted_ptf = deleted_ptf_name

    def add_portfolio(self, name, cash, date, currency):
        """
        This method is used to add a new portfolio item to the portfolio list.

        Parameters
        ----------
        name : `str`
            Name of the portfolio.
        cash : `float`
            Starting balance of the portfolio.
        date : `str`
            Starting date of the portfolio.
        currency : `str`
            Currency of the portfolio. Default is USD.
        """
        portfolio_item = StandardItem(name, cash, date, currency, 10)
        self.portfolio_list.appendRow(portfolio_item)

    def delete_portfolio(self):
        """
        This method is used to delete portfolio from the QTreeView. Method doesn't produce anything if no item is
        selected, otherwise dialog box is produced to validate deletion.
        """
        index = self.currentIndex()
        selection = index.row()
        if index.model() is None:
            pass
        else:
            confirm = QMessageBox.question(self, "Confirm Delete Portfolio Request",
                                           f"Delete this portfolio - {index.data()}?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                if selection == 0:
                    QMessageBox.information(self, "Warning!", "Cannot delete the main portfolio!")
                else:
                    self._deleted_ptf = self.portfolio_list.child(selection).text()
                    index.model().removeRow(selection, index.parent())

    def list_portfolios(self):
        """
        This method produces a list of created portfolios. Used to define dropdown box in the ribbon.

        Returns
        -------
        `list`
            List of portfolio names.
        """
        names = []
        for i in range(self.portfolio_list.rowCount()):
            names.append(self.portfolio_list.child(i).text())

        return names

    @staticmethod
    def get_value(val):
        """
        Returns dictionary of the item data.

        Returns
        -------
        `dict`
            Dictionary of the ptf item data.
        """
        data_dict = {"Ptf_Name": val.data(Qt.ItemDataRole.UserRole),
                     "Ptf_Cash": val.data(Qt.ItemDataRole.UserRole+1),
                     "Ptf_Start": val.data(Qt.ItemDataRole.UserRole+2),
                     "Ptf_Curr": val.data(Qt.ItemDataRole.UserRole+3)}

        print(data_dict)
