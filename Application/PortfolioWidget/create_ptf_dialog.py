from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QLineEdit, QDateTimeEdit, QGridLayout, QMessageBox, \
    QComboBox
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import QDate


class CreatePortfolio(QDialog):
    """
    This class is used to open a new portfolio creation dialog box. It's called in the main window widget by clicking
    on 'Create New Portfolio' button.
    """
    def __init__(self, parent=None, portfolios_list=None):
        super().__init__(parent)

        self.portfolios_list = portfolios_list
        self.setWindowTitle("Create a New Portfolio")

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        name_label = QLabel("Portfolio Name:")
        self.name_edit = QLineEdit()

        cash_label = QLabel("Initial Balance:")
        self.cash_edit = QLineEdit()
        self.cash_edit.setText("100000")
        self.cash_edit.setValidator(QDoubleValidator(0.0, 999999999.99, 2))

        date_label = QLabel("Start Date:")
        self.date_edit = QDateTimeEdit(QDate.currentDate(), calendarPopup=True)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')

        curr_label = QLabel("Currency:")
        self.curr_edit = QComboBox()
        self.curr_edit.addItem("USD")

        selection_layout = QGridLayout()
        selection_layout.addWidget(name_label, 0, 0)
        selection_layout.addWidget(self.name_edit, 0, 1)
        selection_layout.addWidget(cash_label, 1, 0)
        selection_layout.addWidget(self.cash_edit, 1, 1)
        selection_layout.addWidget(date_label, 2, 0)
        selection_layout.addWidget(self.date_edit, 2, 1)
        selection_layout.addWidget(curr_label, 3, 0)
        selection_layout.addWidget(self.curr_edit, 3, 1)
        selection_layout.addWidget(self.button_box, 4, 1)

        self.setLayout(selection_layout)

    def input_check(self):
        """
        This method validates dialog box inputs. Fields cannot be empty.

        Returns
        -------
        `bool`
            Returns True is the check is passed and False otherwise.
        """
        if self.name_edit.text() == "":
            QMessageBox.information(self, "Warning!", "Portfolio name cannot be blank")
            return False
        elif self.name_edit.text() in self.portfolios_list:
            QMessageBox.information(self, "Warning!", "Portfolio already exists!")
            return False
        elif float(self.cash_edit.text()) < 1000:
            QMessageBox.information(self, "Warning!", "Portfolio cash cannot be less than 1000")
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
        Returns the new portfolio name.

        Returns
        -------
        `str`
            Ptf name.
        """
        return self.name_edit.text()

    @property
    def get_ptf_cash(self):
        """
        Returns the new portfolio initial cash balance.

        Returns
        -------
        `float`
            Cash balance.
        """
        return float(self.cash_edit.text())

    @property
    def get_ptf_date(self):
        """
        Returns the new portfolio start date.

        Returns
        -------
        `str`
            Start date of the new ptf.
        """
        return self.date_edit.text()

    @property
    def get_ptf_curr(self):
        """
        Returns the new portfolio currency.

        Returns
        -------
        `str`
            Currency of the new ptf.
        """
        return self.curr_edit.currentText()
