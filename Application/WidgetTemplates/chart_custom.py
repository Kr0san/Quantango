from PyQt6 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib import cm
import matplotlib.dates as mdates
import matplotlib
from matplotlib.ticker import PercentFormatter
import matplotlib.pyplot as plt
import quantstats as qs
import seaborn as sns

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
    def __init__(self, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        self.ax.xaxis.grid(linestyle=':')
        self.ax.yaxis.grid(linestyle=':')
        super(MplCanvas, self).__init__(fig)


class ChartWidget(QtWidgets.QWidget):

    # Class variables for plotting data on the chart widget canvas object (MplCanvas).
    start_date = None
    returns_series = None
    portfolio_label = None
    benchmark_label = None

    def __init__(self):
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
            ptf_ret = filtered_data['Total Equity'].pct_change().fillna(0.0)
            bmk_ret = filtered_data['Benchmark'].pct_change().fillna(0.0)
            x_data = filtered_data.index

            if metric == "Equity":
                if source == "Portfolio":
                    sns.lineplot(data=filtered_data['Total Equity'], ax=self.canvas.ax, label=self.portfolio_label)
                elif source == "Benchmark":
                    sns.lineplot(data=filtered_data['Benchmark'], ax=self.canvas.ax, label=self.benchmark_label)
                else:
                    sns.lineplot(data=filtered_data[['Total Equity', 'Benchmark']], ax=self.canvas.ax, dashes=False)

                self.canvas.ax.set_ylabel(f"{source} Equity")
                self.canvas.ax.format_coord = lambda x, y: f"Date = {mdates.num2date(x).strftime('%Y-%m-%d')} " \
                                                           f"{source} Equity = {y:,.2f}"
                
            elif metric == "Performance":
                if source == "Portfolio":
                    sns.lineplot(data=(ptf_ret.add(1).cumprod() - 1) * 100,
                                 ax=self.canvas.ax, label=self.portfolio_label)
                elif source == "Benchmark":
                    sns.lineplot(data=(bmk_ret.add(1).cumprod() - 1) * 100,
                                 ax=self.canvas.ax, label=self.benchmark_label)
                else:
                    sns.lineplot(data=(ptf_ret.add(1).cumprod() - 1) * 100,
                                 ax=self.canvas.ax, label=self.portfolio_label)
                    sns.lineplot(data=(bmk_ret.add(1).cumprod() - 1) * 100,
                                 ax=self.canvas.ax, label=self.benchmark_label)

                self.canvas.ax.set_ylabel(f"{source} Performance")
                self.canvas.ax.yaxis.set_major_formatter(PercentFormatter())
                self.canvas.ax.format_coord = lambda x, y: f"Date = {mdates.num2date(x).strftime('%Y-%m-%d')} " \
                                                           f"{source} Performance = {y:,.2f} %"

            elif metric == "Drawdown":
                if source == "Portfolio":
                    y_drawdown = qs.stats.to_drawdown_series(ptf_ret)
                    self.canvas.ax.fill_between(x_data, y_drawdown, label=self.portfolio_label, alpha=0.5)
                elif source == "Benchmark":
                    y_drawdown = qs.stats.to_drawdown_series(bmk_ret)
                    self.canvas.ax.fill_between(x_data, y_drawdown, label=self.benchmark_label, alpha=0.5)
                else:
                    y_drawdown = qs.stats.to_drawdown_series(ptf_ret)
                    self.canvas.ax.fill_between(x_data, y_drawdown, label=self.portfolio_label, alpha=0.5)
                    y_drawdown = qs.stats.to_drawdown_series(bmk_ret)
                    self.canvas.ax.fill_between(x_data, y_drawdown, label=self.benchmark_label, alpha=0.5)

                self.canvas.ax.set_ylabel(f"{source} Drawdown")
                self.canvas.ax.yaxis.set_major_formatter(PercentFormatter())
                self.canvas.ax.format_coord = lambda x, y: f"Date = {mdates.num2date(x).strftime('%Y-%m-%d')} " \
                                                           f"{source} Drawdown = {y:,.2f} %"

            self.canvas.ax.yaxis.get_label().set_fontsize(8)
            self.canvas.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            self.canvas.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
            self.canvas.figure.autofmt_xdate()
            self.canvas.ax.tick_params(axis='x', rotation=30, labelsize=7, which='major')
            self.canvas.ax.set_xlabel(None)
            self.canvas.ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15),
                                  bbox_transform=self.canvas.ax.transAxes, ncol=2)

            self.canvas.draw()

    def plot_returns_distribution(self, start_date=None, source="Portfolio"):
        self.canvas.ax.clear()
        self.start_date = start_date

        if self.returns_series is not None:
            filtered_data = self.returns_series.loc[self.start_date:]
            ptf_ret = filtered_data['Total Equity'].pct_change().fillna(0.0)
            bmk_ret = filtered_data['Benchmark'].pct_change().fillna(0.0)

            if source == "Portfolio":
                sns.histplot(ptf_ret, kde=True, ax=self.canvas.ax, label=self.portfolio_label)

            elif source == "Benchmark":
                sns.histplot(bmk_ret, kde=True, ax=self.canvas.ax, label=self.benchmark_label)

            else:
                sns.kdeplot(ptf_ret, fill=True, ax=self.canvas.ax, label=self.portfolio_label)
                sns.kdeplot(bmk_ret, fill=True, ax=self.canvas.ax, label=self.benchmark_label)

            self.canvas.ax.set_ylabel(f"{source} Ret. Density")
            self.canvas.ax.yaxis.get_label().set_fontsize(8)
            self.canvas.ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}%".format(int(x * 100))))
            self.canvas.ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15),
                                  bbox_transform=self.canvas.ax.transAxes, ncol=2)
            self.canvas.draw()

    def plot_monthly_returns(self, source="Portfolio"):
        self.canvas.ax.clear()

        if self.returns_series is not None:
            if source == "Portfolio":
                monthly_returns = qs.stats.monthly_returns(self.returns_series['Ptf Returns']) * 100
                sns.heatmap(data=monthly_returns, annot=True, fmt="0.2f", linewidth=.5, ax=self.canvas.ax,
                            cbar=False, annot_kws={"size": 8}, center=0, cmap=cm.get_cmap("RdYlGn"))

            elif source == "Benchmark":
                monthly_returns = qs.stats.monthly_returns(self.returns_series['Bmk Returns']) * 100
                sns.heatmap(data=monthly_returns, annot=True, fmt="0.2f", linewidth=.5, ax=self.canvas.ax,
                            cbar=False, annot_kws={"size": 8}, center=0, cmap=cm.get_cmap("RdYlGn"))

            else:
                active_returns = qs.stats.monthly_returns(self.returns_series['Ptf Returns']) - \
                                 qs.stats.monthly_returns(self.returns_series['Bmk Returns']) * 100
                sns.heatmap(data=active_returns, annot=True, fmt="0.2f", linewidth=.5, ax=self.canvas.ax,
                            cbar=False, annot_kws={"size": 8}, center=0, cmap=cm.get_cmap("RdYlGn"))

            self.canvas.ax.set_title(f'Monthly {source} Returns (%)', fontweight='bold')
            self.canvas.ax.set_ylabel(None)
            self.canvas.ax.set_yticklabels(self.canvas.ax.get_yticklabels(), rotation=0)
            self.canvas.ax.set_xlabel(None)
            self.canvas.draw()

    def plot_rolling_volatility(self, source="Portfolio", rolling_period=63):
        self.canvas.ax.clear()

        if self.returns_series is not None:
            if source == "Portfolio":
                rolling_volatility = (qs.stats.rolling_volatility(self.returns_series['Ptf Returns'],
                                                                  rolling_period=rolling_period) * 100)
                sns.lineplot(data=rolling_volatility, ax=self.canvas.ax, label=self.portfolio_label)

            elif source == "Benchmark":
                rolling_volatility = (qs.stats.rolling_volatility(self.returns_series['Bmk Returns'],
                                                                  rolling_period=rolling_period) * 100)
                sns.lineplot(data=rolling_volatility, ax=self.canvas.ax, label=self.benchmark_label)

            else:
                rolling_volatility = (qs.stats.rolling_volatility(self.returns_series['Ptf Returns'],
                                                                  rolling_period=rolling_period) * 100)
                sns.lineplot(data=rolling_volatility, ax=self.canvas.ax, label=self.portfolio_label)
                rolling_volatility = (qs.stats.rolling_volatility(self.returns_series['Bmk Returns'],
                                                                  rolling_period=rolling_period) * 100)
                sns.lineplot(data=rolling_volatility, ax=self.canvas.ax, label=self.benchmark_label)

            self.canvas.ax.set_ylabel(f'{source} Rolling {rolling_period}-Day Volatility (%)')
            self.canvas.ax.yaxis.get_label().set_fontsize(8)
            self.canvas.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            self.canvas.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
            self.canvas.figure.autofmt_xdate()
            self.canvas.ax.tick_params(axis='x', rotation=30, labelsize=7, which='major')
            self.canvas.ax.set_xlabel(None)
            self.canvas.ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15),
                                  bbox_transform=self.canvas.ax.transAxes, ncol=2)
            self.canvas.draw()

    def plot_rolling_beta(self, rolling_period=63):
        self.canvas.ax.clear()

        if self.returns_series is not None:
            rolling_greeks = qs.stats.rolling_greeks(self.returns_series['Ptf Returns'],
                                                     self.returns_series['Bmk Returns'], periods=rolling_period)
            sns.lineplot(data=rolling_greeks['beta'], ax=self.canvas.ax, label='Beta')

            self.canvas.ax.set_ylabel(f'Rolling {rolling_period}-Day Beta')
            self.canvas.ax.yaxis.get_label().set_fontsize(8)
            self.canvas.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            self.canvas.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
            self.canvas.figure.autofmt_xdate()
            self.canvas.ax.tick_params(axis='x', rotation=30, labelsize=7, which='major')
            self.canvas.ax.set_xlabel(None)
            self.canvas.ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15),
                                  bbox_transform=self.canvas.ax.transAxes, ncol=2)
            self.canvas.draw()
