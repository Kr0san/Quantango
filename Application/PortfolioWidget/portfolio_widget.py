import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QMainWindow, QScrollArea, QWidget, QTableView, QHBoxLayout, QVBoxLayout, QGroupBox, \
    QHeaderView, QMessageBox, QLabel, QComboBox, QPushButton, QTabWidget
from PyQt6.QtCore import QItemSelectionModel
from Infrastructure.portfolio_constructor import PortfolioConstructor, yf
from Infrastructure.Utilities.business_day_check import BDay
from Application.WidgetTemplates.pandas_table_model import PandasModel
from Application.WidgetTemplates.chart_custom import ChartWidget
from datetime import date
yf.pdr_override()


class PortfolioWidget(QMainWindow):
    def __init__(self, portfolio_name, starting_balance, starting_date, portfolio_currency):
        super().__init__()
        self.ptf_name = portfolio_name
        self.ptf_cash = starting_balance
        self.ptf_start = starting_date
        self.ptf_curr = portfolio_currency
        self.setObjectName(self.ptf_name)

        # Portfolio metrics table placeholders
        self.prop_table = None
        self.prop_model = None
        self.prop_data = [[self.ptf_name, self.ptf_start, self.ptf_cash, None, None, None, None, None]]
        self.prop_headers = ['Name', 'Start Date', 'Balance', 'Total MV', 'Total Equity', 'Total UPL', 'Total RPL',
                             'Total PnL']
        self.prop_dataframe = pd.DataFrame(self.prop_data, columns=self.prop_headers)

        self.prop2_table = None
        self.prop2_model = None
        self.prop2_data = None
        self.prop2_headers = ['Alpha', 'Beta', 'Information Ratio', 'Treynor Ratio',
                              'R-Squared', 'Up Capture', 'Down Capture', 'Batting Ratio']
        self.prop2_dataframe = pd.DataFrame(self.prop2_data, columns=self.prop2_headers)

        # Returns  metrics table placeholders
        self.distribution_metrics_table = None
        self.distribution_metrics_model = None
        self.distribution_metrics_data = np.full((10, 2), None)
        self.distribution_metrics_headers = ['Cum. Return', 'CAGR', 'Ex. Return (D)', 'Ex. Return (M)',
                                             'Ex. Return (Y)', 'MTD Return',
                                             '3M Return', '6M Return', 'YTD Return', '1Y Return']
        self.distribution_metrics_dataframe = pd.DataFrame(self.distribution_metrics_data,
                                                           columns=['Portfolio', 'Benchmark'],
                                                           index=self.distribution_metrics_headers)

        # Performance metrics table placeholders
        self.performance_metrics_table = None
        self.performance_metrics_model = None
        self.performance_metrics_data = np.full((10, 2), None)
        self.performance_metrics_headers = ['Sharpe Ratio', 'Sortino Ratio', 'Omega Ratio', 'Kelly Criterion',
                                            'Payoff Ratio', 'Calmar Ratio', 'CPC Index', 'Outlier Win',
                                            'Outlier Loss', 'Tail Ratio']
        self.performance_metrics_dataframe = pd.DataFrame(self.performance_metrics_data,
                                                          columns=['Portfolio', 'Benchmark'],
                                                          index=self.performance_metrics_headers)

        # Risk metrics table placeholders
        self.risk_metrics_table = None
        self.risk_metrics_model = None
        self.risk_metrics_data = np.full((10, 2), None)
        self.risk_metrics_headers = ['VaR', 'cVaR', 'Risk of Ruin', 'Volatility', 'Skewness', 'Kurtosis',
                                     'Max DD', 'DD Duration', 'Avg. DD', 'Rec. Factor']
        self.risk_metrics_dataframe = pd.DataFrame(self.risk_metrics_data,
                                                   columns=['Portfolio', 'Benchmark'],
                                                   index=self.risk_metrics_headers)

        # Position table placeholders
        self.pos_table = None
        self.pos_model = None
        self.pos_proxy_model = None
        self.pos_data = None
        self.pos_headers = ['Symbol', 'Quantity', 'Market Price', 'Market Value', 'Avg Price', 'Total Cost',
                            'Unrealized PL', 'Realized PL', 'Total PL', 'Holding Date']
        self.pos_dataframe = pd.DataFrame(self.pos_data, columns=self.pos_headers)

        # Transaction table placeholders
        self.trans_table = None
        self.trans_model = None
        self.trans_proxy_model = None
        self.transaction_data = None
        self.trans_headers = ['Symbol', 'Quantity', 'Price', 'Date', 'Commission']
        self.trans_dataframe = pd.DataFrame(self.transaction_data, columns=self.trans_headers)

        # Placeholder for the returns series, benchmark series, first transaction date and the chart
        self.returns_series = None
        self.first_transaction = None
        self.source_combo = None
        self.equity_chart = ChartWidget()
        self.performance_chart = ChartWidget()
        self.drawdown_chart = ChartWidget()
        
        self.main_layout()

    def chart_layout(self):
        source_options_box = QGroupBox()
        source_options_layout = QHBoxLayout()
        source_label = QLabel("Source:")
        self.source_combo = QComboBox()
        self.source_combo.addItems(["Portfolio", "Benchmark", "Portfolio vs Benchmark"])
        self.source_combo.currentIndexChanged.connect(
            lambda: self.update_plots(start_date=self.first_transaction, source=self.source_combo.currentText()))
        self.source_combo.setStatusTip("Select data source to plot. Portfolio, benchmark or both.")

        source_options_layout.addWidget(source_label)
        source_options_layout.addWidget(self.source_combo)
        source_options_box.setLayout(source_options_layout)

        timeline_box = QGroupBox("Timeline:")
        timeline_box_layout = QHBoxLayout()
        itd_button = QPushButton("ITD")
        itd_button.setStatusTip("Plot data inception to date.")
        itd_button.clicked.connect(self.plot_inception_to_date)
        ytd_button = QPushButton("YTD")
        ytd_button.setStatusTip("Plot data year to date.")
        ytd_button.clicked.connect(self.plot_year_to_date)
        mtd_button = QPushButton("MTD")
        mtd_button.setStatusTip("Plot data month to date.")
        mtd_button.clicked.connect(self.plot_month_to_date)
        timeline_box_layout.addWidget(itd_button)
        timeline_box_layout.addWidget(ytd_button)
        timeline_box_layout.addWidget(mtd_button)
        timeline_box.setLayout(timeline_box_layout)

        plot_options_layout = QHBoxLayout()
        plot_options_layout.addWidget(source_options_box)
        plot_options_layout.addWidget(timeline_box)
        # plot_options_layout.setContentsMargins(100, 0, 100, 0)

        plots_tab = QTabWidget()
        plots_tab.addTab(self.equity_chart, "EQUITY")
        plots_tab.addTab(self.performance_chart, "PERFORMANCE")
        plots_tab.addTab(self.drawdown_chart, "DRAWDOWN")

        portfolio_visualization_group = QGroupBox("Portfolio Visualization")
        portfolio_visualization_group_layout = QVBoxLayout()
        portfolio_visualization_group_layout.addLayout(plot_options_layout)
        portfolio_visualization_group_layout.addWidget(plots_tab)
        portfolio_visualization_group.setLayout(portfolio_visualization_group_layout)

        return portfolio_visualization_group

    def portfolio_properties_table(self):
        """
        This method creates a layout for the summary of the initial portfolio properties. Specifically name,
        cash, starting date and currency.

        Returns
        -------
        `QGroupBox`
            Group box layout containing table with portfolio properties.
        """
        self.prop_table = QTableView()
        self.prop_table.verticalHeader().setVisible(False)
        self.prop_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.prop_model = PandasModel(self.prop_dataframe)
        self.prop_table.setModel(self.prop_model)

        self.prop2_table = QTableView()
        self.prop2_table.verticalHeader().setVisible(False)
        self.prop2_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.prop2_model = PandasModel(self.prop2_dataframe)
        self.prop2_table.setModel(self.prop2_model)

        portfolio_properties_group = QGroupBox("Portfolio Metrics")
        portfolio_properties_group_layout = QVBoxLayout()
        portfolio_properties_group_layout.addWidget(self.prop_table)
        portfolio_properties_group_layout.addWidget(self.prop2_table)
        portfolio_properties_group.setLayout(portfolio_properties_group_layout)
        portfolio_properties_group.setMaximumHeight(140)

        return portfolio_properties_group

    def returns_distribution_metrics_table(self):
        self.distribution_metrics_table = QTableView()
        self.distribution_metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.distribution_metrics_model = PandasModel(self.distribution_metrics_dataframe)
        self.distribution_metrics_table.setModel(self.distribution_metrics_model)

        returns_distribution_metrics_group = QGroupBox("Returns Metrics")
        returns_distribution_metrics_group_layout = QVBoxLayout()
        returns_distribution_metrics_group_layout.addWidget(self.distribution_metrics_table)
        returns_distribution_metrics_group.setLayout(returns_distribution_metrics_group_layout)

        return returns_distribution_metrics_group

    def performance_distribution_metrics_table(self):
        self.performance_metrics_table = QTableView()
        self.performance_metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.performance_metrics_model = PandasModel(self.performance_metrics_dataframe)
        self.performance_metrics_table.setModel(self.performance_metrics_model)

        performance_distribution_metrics_group = QGroupBox("Performance Metrics")
        performance_distribution_metrics_group_layout = QVBoxLayout()
        performance_distribution_metrics_group_layout.addWidget(self.performance_metrics_table)
        performance_distribution_metrics_group.setLayout(performance_distribution_metrics_group_layout)

        return performance_distribution_metrics_group

    def risk_distribution_metrics_table(self):
        self.risk_metrics_table = QTableView()
        self.risk_metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.risk_metrics_model = PandasModel(self.risk_metrics_dataframe)
        self.risk_metrics_table.setModel(self.risk_metrics_model)

        risk_distribution_metrics_group = QGroupBox("Risk Metrics")
        risk_distribution_metrics_group_layout = QVBoxLayout()
        risk_distribution_metrics_group_layout.addWidget(self.risk_metrics_table)
        risk_distribution_metrics_group.setLayout(risk_distribution_metrics_group_layout)

        return risk_distribution_metrics_group

    def positions_table(self):
        """
        This method creates a layout for the positions table.

        Returns
        -------
        `QGroupBox`
            Group box layout containing table with portfolio positions.
        """
        self.pos_table = QTableView()
        self.pos_table.verticalHeader().setVisible(False)
        self.pos_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pos_model = PandasModel(self.pos_dataframe)
        # self.pos_proxy_model = QSortFilterProxyModel()
        # self.pos_proxy_model.setSourceModel(self.pos_model)
        self.pos_table.setModel(self.pos_model)
        self.pos_table.setSortingEnabled(True)

        positions_table_group = QGroupBox("Portfolio Positions")
        positions_table_group_layout = QVBoxLayout()
        positions_table_group_layout.addWidget(self.pos_table)
        positions_table_group.setLayout(positions_table_group_layout)

        return positions_table_group

    def transactions_table(self):
        """
        This method creates a layout for the transactions table. Layout is updated as new transactions are
        added or removed.

        Returns
        -------
        `QGroupBox`
            Group box layout containing table with portfolio positions.
        """
        self.trans_table = QTableView()
        self.trans_table.verticalHeader().setVisible(False)
        self.trans_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.trans_model = PandasModel(self.trans_dataframe)
        self.trans_table.setModel(self.trans_model)
        self.trans_table.setSortingEnabled(True)

        transactions_table_group = QGroupBox("Transactions")
        transactions_table_group_layout = QVBoxLayout()
        transactions_table_group_layout.addWidget(self.trans_table)
        transactions_table_group.setLayout(transactions_table_group_layout)

        return transactions_table_group

    def update_positions_table(self, as_of_date, benchmark):
        """
        Updates positions table with the calculated position information from the transaction data. Also constructs
        benchmark timeseries from the selected benchmark and portfolio start date.
        """
        trades = self.trans_model.dataframe
        if trades.empty:
            QMessageBox.information(self, "Message", "Portfolio has no trades!")
        else:
            try:
                self.first_transaction = trades['Date'].min() - BDay(1)
                constructor = PortfolioConstructor(self.first_transaction, self.ptf_cash, self.ptf_name, self.ptf_curr)
                constructor.construct_portfolio_history(trades, as_of_date)

                # Construct returns series to be used for various metrics and plotting
                self.returns_series = constructor.construct_returns_dataframe(benchmark, as_of_date)

                self.pos_model.dataframe = constructor.holdings_as_of_date
                self.prop_dataframe.loc[0, "Balance"] = constructor.portfolio.cash
                self.prop_dataframe.loc[0, "Total MV"] = constructor.portfolio.total_market_value
                self.prop_dataframe.loc[0, "Total Equity"] = constructor.portfolio.total_equity
                self.prop_dataframe.loc[0, "Total UPL"] = constructor.portfolio.total_unrealised_pnl
                self.prop_dataframe.loc[0, "Total RPL"] = constructor.portfolio.total_realised_pnl
                self.prop_dataframe.loc[0, "Total PnL"] = constructor.portfolio.total_pnl
                self.prop_model.dataframe = self.prop_dataframe

                self.prop2_dataframe = constructor.construct_additional_statistics(self.returns_series["Ptf Returns"],
                                                                                   self.returns_series["Bmk Returns"])
                self.prop2_model.dataframe = self.prop2_dataframe

                # Update returns distribution metrics table
                self.distribution_metrics_dataframe = constructor.construct_statistics(
                    self.returns_series["Ptf Returns"],
                    self.returns_series["Bmk Returns"],
                    metrics="returns")

                self.distribution_metrics_model.dataframe = self.distribution_metrics_dataframe

                # Update performance distribution metrics table
                self.performance_metrics_dataframe = constructor.construct_statistics(
                    self.returns_series["Ptf Returns"],
                    self.returns_series["Bmk Returns"],
                    metrics="performance")

                self.performance_metrics_model.dataframe = self.performance_metrics_dataframe

                # Update risk distribution metrics table
                self.risk_metrics_dataframe = constructor.construct_statistics(self.returns_series["Ptf Returns"],
                                                                               self.returns_series["Bmk Returns"],
                                                                               metrics="risk")
                self.risk_metrics_model.dataframe = self.risk_metrics_dataframe

                # Update portfolio series, benchmark series, first transaction and plot

                ChartWidget.returns_series = self.returns_series
                ChartWidget.portfolio_label = self.ptf_name
                ChartWidget.benchmark_label = benchmark
                self.update_plots(start_date=self.first_transaction, source=self.source_combo.currentText())
                # self.equity_chart.plot_metric(start_date=self.first_transaction,
                #                               source=self.source_combo.currentText(),
                #                               metric="Equity")
                # self.performance_chart.plot_metric(start_date=self.first_transaction,
                #                                    source=self.source_combo.currentText(),
                #                                    metric="Performance")

            except Exception as exception:
                QMessageBox.information(self, f"Error!", f"Error computing portfolio: {exception}")

    def insert_transaction_row(self, new_transaction_data):
        """
        This method inserts a new transaction into the trade table. It's called from the MainWindow instance.

        Parameters
        ----------
        new_transaction_data : `list`
            List containing new trade data. Must contain data corresponding to trade table headers.
        """
        self.trans_model.insertRows(self.trans_model.rowCount(), 1, new_data=new_transaction_data)

    def delete_transaction_row(self):
        """
        This method deletes selected trade from the transaction data list. Designed to do nothing if no row in the
        trade table is selected. 
        """
        index = self.trans_table.selectionModel().selectedIndexes()
        if index:
            confirm = QMessageBox.question(self, "Confirm Delete Trade Request",
                                           "Delete selected trade from the transactions list?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.trans_model.removeRows(index[0].row(), 1)
                self.trans_table.selectionModel().select(self.trans_table.selectionModel().selection(),
                                                         QItemSelectionModel.SelectionFlag.Deselect)

    def import_trade_file_dataframe(self, file):
        """
        Imports trade file. Must be in .csv format and contain headers corresponding to trade table headers.

        Parameters
        ----------
        file : `str`
            Name of the trade file. Passed from MainWindow instance.
        """
        df = pd.read_csv(file)
        if all(header in df.columns for header in self.trans_headers):
            df["Date"] = pd.to_datetime(df["Date"], format='%Y-%m-%d', dayfirst=True)
            self.trans_model.dataframe = df
        else:
            QMessageBox.information(self, "Error!", "Imported file headers do not match transaction table headers!")

    def export_trade_file_dataframe(self, file_name):
        """
        Export file containing current transaction data.

        Parameters
        ----------
        file_name : `str`
            Name of the trade file to be exported. Name should contain .csv extension.
        """
        df = self.trans_model.dataframe
        df.to_csv(file_name, index=False)

    def plot_inception_to_date(self):
        """
        Re-plots portfolio data from the first transaction date - 1 to as of date.
        """
        self.update_plots(start_date=self.first_transaction, source=self.source_combo.currentText())

    def plot_month_to_date(self):
        """
        Re-plots portfolio data from the start of the latest month to as of date.
        """
        if self.returns_series is not None:
            max_as_of_date = self.returns_series.index.max()
            start_date = pd.to_datetime(date(max_as_of_date.year, max_as_of_date.month, 1), dayfirst=True)
            self.update_plots(start_date=start_date - BDay(1), source=self.source_combo.currentText())

    def plot_year_to_date(self):
        """
        Re-plots portfolio data from the start of the latest year to as of date. If the start of the
        latest year is before the first transaction then the data is simply re-ploted as inception to as of date.
        """
        if self.returns_series is not None:
            max_as_of_date = self.returns_series.index.max()
            start_date = pd.to_datetime(date(max_as_of_date.year, 1, 1), dayfirst=True)
            if start_date >= self.first_transaction:
                self.update_plots(start_date=start_date - BDay(1), source=self.source_combo.currentText())
            else:
                self.plot_inception_to_date()

    def update_plots(self, start_date, source):
        self.equity_chart.plot_metric(start_date=start_date, source=source, metric="Equity")
        self.performance_chart.plot_metric(start_date=start_date, source=source, metric="Performance")
        self.drawdown_chart.plot_metric(start_date=start_date, source=source, metric="Drawdown")

    def statistics_layout(self):
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.returns_distribution_metrics_table())
        horizontal_layout.addWidget(self.performance_distribution_metrics_table())
        horizontal_layout.addWidget(self.risk_distribution_metrics_table())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.portfolio_properties_table())
        vertical_layout.addLayout(horizontal_layout)

        return vertical_layout

    def main_layout(self):
        """
        Defines main layout using upper and lower layout settings.
        """
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        main_widget = QWidget()
        main_widget_layout = QVBoxLayout()

        upper_layout = QHBoxLayout()
        upper_layout.addLayout(self.statistics_layout(), stretch=6)
        upper_layout.addWidget(self.chart_layout(), stretch=5)

        lower_layout = QHBoxLayout()
        lower_layout.addWidget(self.positions_table(), stretch=4)
        lower_layout.addWidget(self.transactions_table(), stretch=2)

        main_widget_layout.addLayout(upper_layout)
        main_widget_layout.addLayout(lower_layout)

        main_widget.setLayout(main_widget_layout)
        scroll_area.setWidget(main_widget)
        self.setCentralWidget(scroll_area)
