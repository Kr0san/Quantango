from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QLineEdit, QDateTimeEdit, QGridLayout, QMessageBox, \
    QComboBox
from PyQt6.QtGui import QDoubleValidator
from Infrastructure.Utilities.business_day_check import is_business_day
from pandas.tseries.offsets import BDay
import pandas as pd
import datetime


class NewSubRed(QDialog):
    def __init__(self, parent=None, portfolios_list=None, transaction="subscription"):
        super(NewSubRed, self).__init__(parent)
        self.trans_type = transaction
        self.setWindowTitle(f"Create a new {self.trans_type}")
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.ptf_list = portfolios_list
        ptf_list_label = QLabel("Portfolio")
        self.ptf_list_dropdown = QComboBox()
        for item in self.ptf_list:
            self.ptf_list_dropdown.addItem(item)

        transaction_label = QLabel("Transaction")
        self.transaction_edit = QLineEdit(self.trans_type.upper())
        self.transaction_edit.setReadOnly(True)
        amount_label = QLabel("Amount")
        self.amount_edit = QLineEdit("1000")
        self.amount_edit.setValidator(QDoubleValidator(0, 999999999.0, 2))

        date_label = QLabel("Start Date:")
        date_selection = datetime.datetime.today() - BDay(1)
        self.date_edit = QDateTimeEdit(date_selection, calendarPopup=True)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')

        new_trade_layout = QGridLayout()
        new_trade_layout.addWidget(ptf_list_label, 0, 0)
        new_trade_layout.addWidget(self.ptf_list_dropdown, 0, 1)
        new_trade_layout.addWidget(transaction_label, 1, 0)
        new_trade_layout.addWidget(self.transaction_edit, 1, 1)
        new_trade_layout.addWidget(amount_label, 2, 0)
        new_trade_layout.addWidget(self.amount_edit, 2, 1)
        new_trade_layout.addWidget(date_label, 3, 0)
        new_trade_layout.addWidget(self.date_edit, 3, 1)
        new_trade_layout.addWidget(self.button_box, 4, 1)

        self.setLayout(new_trade_layout)

    def input_check(self):
        """
        This method validates dialog box inputs.

        Returns
        -------
        `bool`
            Returns True is the check is passed and False otherwise.
        """

        if not is_business_day(self.date_edit.text()):
            QMessageBox.information(self, "Warning!", 
                                    f"{self.trans_type.capitalize()} date cannot be a non-business day!")
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
    def get_transaction(self):
        """
        Returns transaction type.

        Returns
        -------
        `str`
            SUBSCRIPTION or WITHDRAWAL.
        """
        return self.transaction_edit.text()
    
    @property
    def get_amount(self):
        """
        Returns amount of subscription or withdrawal.

        Returns
        -------
        `float`
            Amount of subscription/withdrawal..
        """
        return float(self.amount_edit.text())

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
    