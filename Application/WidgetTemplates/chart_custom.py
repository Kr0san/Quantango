from PyQt6 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib
from matplotlib.ticker import PercentFormatter
import matplotlib.pyplot as plt
import quantstats as qs

from qbstyles import mpl_style
mpl_style(dark=True)

matplotlib.use('QtAgg')
# plt.style.use('dark_background')
plt.rcParams['axes.facecolor'] = '#101012'
plt.rcParams['figure.facecolor'] = '#202124'  # #e4e7eb #202124 8ab4f7 161719


class NavigationToolbar(QtWidgets.QWidget):
    def __init__(self, canvas, parent=None):
        super(NavigationToolbar, self).__init__(parent)

        self.canvas = canvas

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.toolbar.setStyleSheet("background-color: transparent;")

        layout.addWidget(self.toolbar)
        self.setLayout(layout)


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        self.ax.xaxis.grid(linestyle=':')
        self.ax.yaxis.grid(linestyle=':')
        # self.ax.tick_params(reset=True)
        # self.ax.xaxis.set_tick_params(which='major', length=10)
        # self.ax.tick_params(which='major', length=7)
        super(MplCanvas, self).__init__(fig)


class ChartWidget(QtWidgets.QWidget):

    # Class variables for plotting data on the chart widget canvas object (MplCanvas).
    start_date = None
    returns_series = None
    portfolio_label = None
    benchmark_label = None

    def __init__(self, parent=None):
        super().__init__()

        self.canvas = MplCanvas()
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setContentsMargins(50, 0, 50, 0)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)
        self.setLayout(layout)

    def plot_metric(self, start_date=None, source="Portfolio", metric="Equity"):
        self.canvas.ax.clear()
        self.start_date = start_date

        if self.returns_series is not None:
            filtered_data = self.returns_series.loc[self.start_date:]
            x_data = filtered_data.index

            if metric == "Equity":
                if source == "Portfolio":
                    y_data = filtered_data['Total Equity']
                    self.canvas.ax.plot(x_data, y_data, label=self.portfolio_label)
                    self.canvas.ax.set_ylabel("Portfolio Equity")
                    self.canvas.ax.format_coord = lambda x, y: f"Date = {mdates.num2date(x).strftime('%Y-%m-%d')} " \
                                                               f"Portfolio Equity = {y:,.2f}"
                elif source == "Benchmark":
                    y_data = filtered_data['Benchmark']
                    self.canvas.ax.plot(x_data, y_data, label=self.benchmark_label)
                    self.canvas.ax.set_ylabel("Benchmark Equity")
                    self.canvas.ax.format_coord = lambda x, y: f"Date = {mdates.num2date(x).strftime('%Y-%m-%d')} " \
                                                               f"Benchmark Equity = {y:,.2f}"
                else:
                    self.canvas.ax.plot(x_data, filtered_data['Total Equity'], label=self.portfolio_label)
                    self.canvas.ax.plot(x_data, filtered_data['Benchmark'], label=self.benchmark_label)
                    self.canvas.ax.set_ylabel("Ptf vs Bmk Equity")
                    self.canvas.ax.format_coord = lambda x, y: f"Date = {mdates.num2date(x).strftime('%Y-%m-%d')} " \
                                                               f"Equity = {y:,.2f}"
    
                self.canvas.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                self.canvas.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
                self.canvas.figure.autofmt_xdate()
                for label in self.canvas.ax.get_xticklabels(which='major'):
                    label.set(rotation=30, horizontalalignment='right', fontsize=7)
                self.canvas.ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15),
                                          bbox_transform=self.canvas.ax.transAxes, ncol=2)
                
            elif metric == "Performance":
                if source == "Portfolio":
                    y_data = filtered_data['Total Equity']
                    y_data_perf = y_data.pct_change().fillna(0.0)
                    self.canvas.ax.plot(x_data, (y_data_perf.add(1).cumprod() - 1) * 100, label=self.portfolio_label)
                    self.canvas.ax.set_ylabel("Portfolio Performance")
                    self.canvas.ax.yaxis.set_major_formatter(PercentFormatter())
                    self.canvas.ax.format_coord = lambda x, y: f"Date = {mdates.num2date(x).strftime('%Y-%m-%d')} " \
                                                               f"Portfolio Performance = {y:,.2f} %"
                elif source == "Benchmark":
                    y_data = filtered_data['Benchmark']
                    y_data_perf = y_data.pct_change().fillna(0.0)
                    self.canvas.ax.plot(x_data, (y_data_perf.add(1).cumprod() - 1) * 100, label=self.benchmark_label)
                    self.canvas.ax.set_ylabel("Benchmark Performance")
                    self.canvas.ax.yaxis.set_major_formatter(PercentFormatter())
                    self.canvas.ax.format_coord = lambda x, y: f"Date = {mdates.num2date(x).strftime('%Y-%m-%d')} " \
                                                               f"Benchmark Performance = {y:,.2f} %"
                else:
                    y_data = filtered_data['Total Equity']
                    y_data_perf = y_data.pct_change().fillna(0.0)
                    self.canvas.ax.plot(x_data, (y_data_perf.add(1).cumprod() - 1) * 100, label=self.portfolio_label)
                    y_data = filtered_data['Benchmark']
                    y_data_perf = y_data.pct_change().fillna(0.0)
                    self.canvas.ax.plot(x_data, (y_data_perf.add(1).cumprod() - 1) * 100, label=self.benchmark_label)
                    self.canvas.ax.set_ylabel("Ptf vs Bmk Performance")
                    self.canvas.ax.yaxis.set_major_formatter(PercentFormatter())
                    self.canvas.ax.format_coord = lambda x, y: f"Date = {mdates.num2date(x).strftime('%Y-%m-%d')} " \
                                                               f"Performance = {y:,.2f} %"

            elif metric == "Drawdown":
                if source == "Portfolio":
                    y_data = filtered_data['Total Equity']
                    y_data_perf = y_data.pct_change().fillna(0.0)
                    y_drawdown = qs.stats.to_drawdown_series(y_data_perf)
                    self.canvas.ax.fill_between(x_data, y_drawdown, label=self.portfolio_label, alpha=0.5)
                    self.canvas.ax.set_ylabel("Portfolio Drawdown")
                    self.canvas.ax.yaxis.set_major_formatter(PercentFormatter())
                    self.canvas.ax.format_coord = lambda x, y: f"Date = {mdates.num2date(x).strftime('%Y-%m-%d')} " \
                                                               f"Portfolio Drawdown = {y:,.2f} %"
                elif source == "Benchmark":
                    y_data = filtered_data['Benchmark']
                    y_data_perf = y_data.pct_change().fillna(0.0)
                    y_drawdown = qs.stats.to_drawdown_series(y_data_perf)
                    self.canvas.ax.fill_between(x_data, y_drawdown, label=self.benchmark_label, alpha=0.5)
                    self.canvas.ax.set_ylabel("Benchmark Drawdown")
                    self.canvas.ax.yaxis.set_major_formatter(PercentFormatter())
                    self.canvas.ax.format_coord = lambda x, y: f"Date = {mdates.num2date(x).strftime('%Y-%m-%d')} " \
                                                               f"Benchmark Drawdown = {y:,.2f} %"
                else:
                    y_data = filtered_data['Total Equity']
                    y_data_perf = y_data.pct_change().fillna(0.0)
                    y_drawdown = qs.stats.to_drawdown_series(y_data_perf)
                    self.canvas.ax.fill_between(x_data, y_drawdown, label=self.portfolio_label, alpha=0.5)
                    y_data = filtered_data['Benchmark']
                    y_data_perf = y_data.pct_change().fillna(0.0)
                    y_drawdown = qs.stats.to_drawdown_series(y_data_perf)
                    self.canvas.ax.fill_between(x_data, y_drawdown, label=self.benchmark_label, alpha=0.5)
                    self.canvas.ax.set_ylabel("Ptf vs Bmk Drawdown")
                    self.canvas.ax.yaxis.set_major_formatter(PercentFormatter())
                    self.canvas.ax.format_coord = lambda x, y: f"Date = {mdates.num2date(x).strftime('%Y-%m-%d')} " \
                                                               f"Drawdown = {y:,.2f} %"

            self.canvas.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            self.canvas.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
            self.canvas.figure.autofmt_xdate()
            for label in self.canvas.ax.get_xticklabels(which='major'):
                label.set(rotation=30, horizontalalignment='right', fontsize=7)
            self.canvas.ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15),
                                  bbox_transform=self.canvas.ax.transAxes, ncol=2)

        self.canvas.draw()

    def plot_portfolio_data(self, start_date=None, metric="Total Equity"):
        self.canvas.ax.clear()
        self.start_date = start_date

        if self.returns_series is not None:
            filtered_performance_series = self.returns_series.loc[self.start_date:]
            x_data = filtered_performance_series.index
            y_data_eq = filtered_performance_series['Total Equity']
            y_data_bmk = filtered_performance_series['Benchmark']

            y_data_perf = y_data_eq.pct_change().fillna(0.0)
            y_data_perf_bmk = y_data_bmk.pct_change().fillna(0.0)

            if metric == 'Performance':
                self.canvas.ax.plot(x_data, (y_data_perf.add(1).cumprod() - 1) * 100, label=self.portfolio_label)
                self.canvas.ax.plot(x_data, (y_data_perf_bmk.add(1).cumprod() - 1) * 100, label=self.benchmark_label)
                self.canvas.ax.set_ylabel("Performance")
                self.canvas.ax.yaxis.set_major_formatter(PercentFormatter())
                self.canvas.ax.format_coord = lambda x, y: f"Date = {mdates.num2date(x).strftime('%Y-%m-%d')} " \
                                                           f"Performance = {y:,.2f} %"
            else:
                self.canvas.ax.plot(x_data, y_data_eq, label=self.portfolio_label)
                self.canvas.ax.set_ylabel("Portfolio Equity")
                self.canvas.ax.format_coord = lambda x, y: f"Date = {mdates.num2date(x).strftime('%Y-%m-%d')} " \
                                                           f"Portfolio Equity = {y:,.2f}"

            self.canvas.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            self.canvas.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
            self.canvas.figure.autofmt_xdate()
            for label in self.canvas.ax.get_xticklabels(which='major'):
                label.set(rotation=30, horizontalalignment='right', fontsize=7)
            self.canvas.ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15),
                                      bbox_transform=self.canvas.ax.transAxes, ncol=2)

        self.canvas.draw()
