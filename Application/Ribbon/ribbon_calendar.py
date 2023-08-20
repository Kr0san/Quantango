from PyQt6.QtCore import QDate, pyqtSlot
from PyQt6.QtWidgets import QDateEdit, QPushButton
from pandas.tseries.offsets import BDay
import datetime


class RibbonCalendar(QDateEdit):
    def __init__(self, max_width=50, parent=None):
        super().__init__(parent, calendarPopup=True)
        self.setMinimumWidth(max_width)
        # self.setStyleSheet("border: 1px solid rgba(0,0,0,30%);")
        self._today_button = QPushButton(self.tr("Today"))
        self._today_button.clicked.connect(self._update_today)
        self.calendarWidget().layout().addWidget(self._today_button)
        self.calendarWidget().setStyleSheet("padding: 1px")

        date_selection = datetime.datetime.today() - BDay(1)
        self.setDate(date_selection)

    @pyqtSlot()
    def _update_today(self):
        self._today_button.clearFocus()
        today = QDate.currentDate()
        self.calendarWidget().setSelectedDate(today)
