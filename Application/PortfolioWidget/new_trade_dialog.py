from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QLineEdit, QDateTimeEdit, QGridLayout, QMessageBox, \
    QComboBox
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from Infrastructure.Utilities.business_day_check import is_business_day
from pandas.tseries.offsets import BDay
import pandas as pd
import datetime


class NewTrade(QDialog):
    def __init__(self, parent=None, portfolios_list=None):
        super(NewTrade, self).__init__(parent)
        self.setWindowTitle("Create a New Trade")
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.ptf_list = portfolios_list
        ptf_list_label = QLabel("Portfolio")
        self.ptf_list_dropdown = QComboBox()
        for item in self.ptf_list:
            self.ptf_list_dropdown.addItem(item)

        symbol_label = QLabel("Symbol")
        self.symbol_edit = QLineEdit()
        quantity_label = QLabel("Quantity")
        self.quantity_edit = QLineEdit("1000")
        self.quantity_edit.setValidator(QIntValidator())

        price_label = QLabel("Price")
        self.price_edit = QLineEdit("100")
        self.price_edit.setValidator(QDoubleValidator(0, 999999999.0, 2))

        date_label = QLabel("Start Date:")
        date_selection = datetime.datetime.today() - BDay(1)
        self.date_edit = QDateTimeEdit(date_selection, calendarPopup=True)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')

        commission_label = QLabel("Commission")
        self.commission_edit = QLineEdit("2")
        self.commission_edit.setValidator(QDoubleValidator(0, 999999999.0, 2))

        new_trade_layout = QGridLayout()
        new_trade_layout.addWidget(ptf_list_label, 0, 0)
        new_trade_layout.addWidget(self.ptf_list_dropdown, 0, 1)
        new_trade_layout.addWidget(symbol_label, 1, 0)
        new_trade_layout.addWidget(self.symbol_edit, 1, 1)
        new_trade_layout.addWidget(quantity_label, 2, 0)
        new_trade_layout.addWidget(self.quantity_edit, 2, 1)
        new_trade_layout.addWidget(price_label, 3, 0)
        new_trade_layout.addWidget(self.price_edit, 3, 1)
        new_trade_layout.addWidget(date_label, 4, 0)
        new_trade_layout.addWidget(self.date_edit, 4, 1)
        new_trade_layout.addWidget(commission_label, 5, 0)
        new_trade_layout.addWidget(self.commission_edit, 5, 1)
        new_trade_layout.addWidget(self.button_box, 6, 1)

        self.setLayout(new_trade_layout)

    def input_check(self):
        """
        This method validates dialog box inputs.

        Returns
        -------
        `bool`
            Returns True is the check is passed and False otherwise.
        """
        if self.symbol_edit.text() == "":
            QMessageBox.information(self, "Warning!", "Symbol cannot be blank!")
            return False
        elif not is_business_day(self.date_edit.text()):
            QMessageBox.information(self, "Warning!", "Trade date cannot be a non-business day!")
            return False
        else:
            return True

    def accept(self):
        """
        Overrides accept method in QDialog class. Incorporates validation check defined above.
        """
        valid_input = self.input_check()
        if valid_input:
            self.done(1)

    @property
    def get_ptf_name(self):
        """
        Returns portfolio name from the dropdown box.

        Returns
        -------
        `str`
            Ptf name.
        """
        return self.ptf_list_dropdown.currentText()

    @property
    def get_symbol(self):
        """
        Returns transaction symbol.

        Returns
        -------
        `str`
            Symbol.
        """
        return self.symbol_edit.text()

    @property
    def get_quantity(self):
        """
        Returns transaction quantity. Can be negative if it's a sell/short transaction.

        Returns
        -------
        `int`
            Quantity.
        """
        return int(self.quantity_edit.text())

    @property
    def get_price(self):
        """
        Returns transaction price. Cannot be negative.

        Returns
        -------
        `float`
            Price.
        """
        return float(self.price_edit.text())

    @property
    def get_date(self):
        """
        Returns transaction date.

        Returns
        -------
        `str`
            Date
        """
        return pd.to_datetime(self.date_edit.text(), format='%Y-%m-%d', dayfirst=True)

    @property
    def get_commission(self):
        """
        Returns transaction fee.

        Returns
        -------
        `float`
            Commission.
        """
        return float(self.commission_edit.text())
