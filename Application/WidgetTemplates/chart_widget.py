from PyQt6.QtWidgets import QWidget, QCheckBox, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QToolTip, \
    QMenu, QFileDialog, QDateTimeEdit, QLineEdit, QPushButton, QGroupBox
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PyQt6.QtCore import Qt, pyqtSlot, QDateTime, QDate
from PyQt6.QtGui import QPainter, QCursor
import pandas_datareader as pdr
import datetime


class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super(ChartWidget, self).__init__(parent)
        self.theme_combobox = self.create_theme_box()
        self.animation_combobox = self.create_animation_box()
        self.legend_combobox = self.create_legend_box()
        self.antialias_checkbox = QCheckBox("Anti-aliasing")
        self.antialias_checkbox.setChecked(True)

        self.inception_to_date = QPushButton("ITD", self)
        self.year_to_date = QPushButton("YTD", self)
        self.month_to_date = QPushButton("MTD", self)
        self.week_to_date = QPushButton("WTD", self)

        settings_box = QGroupBox("Plot Settings")
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("Theme:"))
        settings_layout.addWidget(self.theme_combobox)
        settings_layout.addWidget(QLabel("Animation:"))
        settings_layout.addWidget(self.animation_combobox)
        settings_layout.addWidget(QLabel("Legend:"))
        settings_layout.addWidget(self.legend_combobox)
        settings_layout.addWidget(self.antialias_checkbox)
        settings_box.setLayout(settings_layout)

        plot_timeline_box = QGroupBox("Plot Timeline")
        plot_timeline_layout = QHBoxLayout()
        plot_timeline_layout.addWidget(self.inception_to_date)
        plot_timeline_layout.addWidget(self.year_to_date)
        plot_timeline_layout.addWidget(self.month_to_date)
        plot_timeline_layout.addWidget(self.week_to_date)
        plot_timeline_box.setLayout(plot_timeline_layout)

        combined_layout = QHBoxLayout()
        combined_layout.addWidget(settings_box)
        combined_layout.addWidget(plot_timeline_box)

        base_layout = QVBoxLayout()
        base_layout.addLayout(combined_layout)

        self.chart_view = QChartView(QChart())
        base_layout.addWidget(self.chart_view)
        self.connectSignals()
        self.update_plot()
        self.setLayout(base_layout)

    def connectSignals(self):
        self.theme_combobox.currentIndexChanged.connect(self.update_plot)
        self.antialias_checkbox.toggled.connect(self.update_plot)
        self.animation_combobox.currentIndexChanged.connect(self.update_plot)
        self.legend_combobox.currentIndexChanged.connect(self.update_plot)
        # self.plot_button.clicked.connect(self.plot_series)

    def create_theme_box(self):
        theme_combobox = QComboBox()
        theme_combobox.addItem("Dark", QChart.ChartTheme.ChartThemeDark)
        theme_combobox.addItem("Blue Cerulean", QChart.ChartTheme.ChartThemeBlueCerulean)

        return theme_combobox

    def create_animation_box(self):
        animation_combobox = QComboBox()
        animation_combobox.addItem("All Animations", QChart.AnimationOption.AllAnimations)
        animation_combobox.addItem("GridAxis Animations", QChart.AnimationOption.GridAxisAnimations)
        animation_combobox.addItem("Series Animations", QChart.AnimationOption.SeriesAnimations)
        animation_combobox.addItem("No Animations", QChart.AnimationOption.NoAnimation)

        return animation_combobox

    def create_legend_box(self):
        legend_combobox = QComboBox()
        legend_combobox.addItem("No Legend ", 0)
        legend_combobox.addItem("Legend Top", Qt.AlignmentFlag.AlignTop)
        legend_combobox.addItem("Legend Bottom", Qt.AlignmentFlag.AlignBottom)
        legend_combobox.addItem("Legend Left", Qt.AlignmentFlag.AlignLeft)
        legend_combobox.addItem("Legend Right", Qt.AlignmentFlag.AlignRight)

        return legend_combobox

    def on_series_hovered(self, point, state):
        if state:
            t = datetime.datetime.utcfromtimestamp(float(point.x()) / 1000.)
            price = round(point.y(), 2)
            ts_name = self.sender().name()
            QToolTip.showText(QCursor.pos(), f"{ts_name} series\nDate: {t.strftime('%Y-%m-%d')}\nPrice: {price}")
            
    @pyqtSlot()
    def update_plot(self):
        theme = self.theme_combobox.itemData(self.theme_combobox.currentIndex())
        if self.chart_view.chart().theme() != theme:
            self.chart_view.chart().setTheme(theme)

        checked = self.antialias_checkbox.isChecked()
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing, checked)

        options = QChart.AnimationOption(self.animation_combobox.itemData(self.animation_combobox.currentIndex()))
        if self.chart_view.chart().animationOptions() != options:
            self.chart_view.chart().setAnimationOptions(options)

        alignment = self.legend_combobox.itemData(self.legend_combobox.currentIndex())
        legend = self.chart_view.chart().legend()
        if alignment == 0:
            legend.hide()
        else:
            legend.setAlignment(Qt.AlignmentFlag(alignment))
            legend.show()

    @pyqtSlot()
    def plot_series(self, data):
        try:
            if self.chart_view.chart().series():
                # self.chart_view.chart().removeAllSeries()
                prev_series = self.chart_view.chart().series()
                prev_axisX = self.chart_view.chart().axes(Qt.Orientation.Horizontal, prev_series[0])
                prev_axisY = self.chart_view.chart().axes(Qt.Orientation.Vertical, prev_series[0])
                #
                self.chart_view.chart().removeSeries(prev_series[0])
                self.chart_view.chart().removeAxis(prev_axisX[0])
                self.chart_view.chart().removeAxis(prev_axisY[0])

            series = QLineSeries()
            series.hovered.connect(self.on_series_hovered)
            series.setName("Test")

            date = self.date_transform(data["Date"])
            prices = data["Total Equity"]

            for i, e in zip(date, prices):
                series.append(i.toMSecsSinceEpoch(), float(e))

            self.chart_view.chart().addSeries(series)
            self.chart_view.chart().setTitle("Portfolio History")

            axisY = QValueAxis()
            axisY.setLabelFormat("%.2f")

            axisX = QDateTimeAxis()
            axisX.setLabelsAngle(45)
            axisX.setFormat("dd-MM-yyyy")
            axisX.setTitleText("Date")

            self.chart_view.chart().addAxis(axisX, Qt.AlignmentFlag.AlignBottom)
            series.attachAxis(axisX)
            self.chart_view.chart().addAxis(axisY, Qt.AlignmentFlag.AlignLeft)
            series.attachAxis(axisY)

        except Exception as e:
            print(e)

    @staticmethod
    def date_transform(dates):
        date_range = []
        for i in dates:
            qtdate = QDateTime(i.year, i.month, i.day, i.hour, i.minute)
            date_range.append(qtdate)

        return date_range

    # def contextMenuEvent(self, event):
    #     try:
    #         cmenu = QMenu(self)
    #         saveAct = cmenu.addAction("Save as")
    #         action = cmenu.exec_(self.mapToGlobal(event.pos()))
    #         if action == saveAct:
    #             filename, _ = QFileDialog.getSaveFileName(self)
    #             pixmap = self.chart_view.grab()
    #             if pixmap is not None and filename:
    #                 pixmap.save(filename)
    #     except Exception as e:
    #         print(e)


# if __name__ == '__main__':
#
#     import sys
#
#     from PyQt6.QtWidgets import QApplication, QMainWindow
#
#     app = QApplication(sys.argv)
#
#     window = QMainWindow()
#     widget = ChartWidget()
#     window.setCentralWidget(widget)
#     window.resize(900, 600)
#     window.show()
#
#     sys.exit(app.exec())
