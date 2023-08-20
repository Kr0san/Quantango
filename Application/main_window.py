from PyQt6.QtWidgets import QMainWindow, QDockWidget, QWidget, QLabel, QTabWidget, QFileDialog, QMessageBox
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSlot, Qt
from Application.Ribbon.ribbon_button import RibbonButton
from Application.Ribbon.icons import get_icon
from Application.Ribbon.ribbon_widget import RibbonWidget
from Application.Ribbon.ribbon_calendar import RibbonCalendar
from Application.Ribbon.ribbon_dropdown import RibbonDropdown
from Application.WidgetTemplates.dock_widget import DockWidget
from Application.PortfolioWidget.portfolio_list import PortfolioList
from Application.PortfolioWidget.create_ptf_dialog import CreatePortfolio
from Application.PortfolioWidget.new_trade_dialog import NewTrade
from Application.PortfolioWidget.ptf_funds_dialog import NewSubRed
from Application.PortfolioWidget.portfolio_widget import PortfolioWidget
import pandas as pd


class MainWindow(QMainWindow):
    """
    This class creates the main window of the application and handles all the actions associated with its components,
    such as docking and action instances.
    """
    def __init__(self):
        QMainWindow.__init__(self)
        self.resize(1350, 800)
        self.showMaximized()
        self.setWindowTitle("QuanTango")
        self.setDockOptions(self.DockOption.AllowNestedDocks | self.DockOption.AllowTabbedDocks)
        self.setTabPosition(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea,
                            QTabWidget.TabPosition.North)
        self.setWindowIcon(get_icon("app_logo"))
        self.statusBar().showMessage('Ready')

        # Portfolio Selection panel

        self._portfolio_tree = PortfolioList()
        self._portfolio_tree.doubleClicked.connect(self.on_portfolio_list_doubleclick)
        self._portfolio_tree_action = self.add_action("Portfolio Tree", "portfolio_list", "Show Portfolio Tree", True,
                                                      self.on_open_portfolio_tree)
        self._portfolio_tree_widget = self.add_dock("Portfolio List", self._portfolio_tree,
                                                    allowed_areas=Qt.DockWidgetArea.LeftDockWidgetArea,
                                                    features=QDockWidget.DockWidgetFeature.DockWidgetClosable,
                                                    delete_on_close=False, is_hidden=True, tabify=False)
        self._portfolio_tree_widget.setMinimumWidth(170)

        self._create_portfolio_action = self.add_action("New Portfolio", "new_portfolio", "Create a New Portfolio",
                                                        True, self.on_create_new_portfolio)

        self._delete_portfolio_action = self.add_action("Delete Portfolio", "delete_portfolio",
                                                        "Delete Selected Portfolio", True, self.on_delete_portfolio)

        # Portfolio Initialization panel

        self._load_portfolio_action = self.add_action("Load Portfolio", "load_portfolio",
                                                      "Initialize Selected Portfolio", True, self.on_load_portfolio)

        self._ptf_dropdown = RibbonDropdown(self._portfolio_tree.list_portfolios())
        self._ptf_dropdown.currentTextChanged.connect(self.on_ptf_dropdown_selection)

        self._bmk_dropdown = RibbonDropdown(['S&P 500', 'NASDAQ', 'Dow Jones', 'Russell 2000', 'Nikkei 225',
                                             'Hang Seng', 'Euro Stoxx 50'])

        # Trade panel

        self._new_trade_action = self.add_action("New Trade", "new_trade",
                                                 "Add a new trade to the Selected Portfolio", True,
                                                 self.on_create_new_trade)

        self._delete_trade_action = self.add_action("Delete Trade", "delete_trade",
                                                    "Delete a selected trade from the Selected Portfolio",
                                                    True, self.on_delete_trade)

        self._import_trades_action = self.add_action("Import Trades", "import_trades",
                                                     "Import a list of transactions from a csv file",
                                                     True, self.on_import_trade_file)

        self._export_trades_action = self.add_action("Export Trades", "export_trades",
                                                     "Export a list of current transactions to a csv file",
                                                     True, self.on_export_trade_file)

        # Portfolio funds panel (subs and reds)

        self._subscribe_funds_action = self.add_action("Subscribe Funds", "subscribe_funds",
                                                       "Subscribe funds to the Selected Portfolio",
                                                       True, lambda: self.on_create_funds_transaction("subscription"))

        self._withdraw_funds_action = self.add_action("Withdraw Funds", "redeem_funds",
                                                      "Withdraw funds from the Selected Portfolio",
                                                      True, lambda: self.on_create_funds_transaction("withdrawal"))

        # Portfolio Dock
        self._main_dock_widget = self.add_dock("Main Portfolio",
                                               PortfolioWidget("Main Portfolio", 100000.0, '2022-01-01', 'USD'),
                                               delete_on_close=False, tabify=False)
        self.tabifiedDockWidgetActivated.connect(self.on_docked_tab_click)

        # Ribbon

        self._calendar = RibbonCalendar()
        self._ribbon = RibbonWidget(self)
        self.addToolBar(self._ribbon)
        self.init_ribbon()

    def add_action(self, caption, icon_name, status_tip, icon_visible, connection, shortcut=None):
        """
        This function is used as a convenience function for action creation.

        Parameters
        ----------
        caption : `str`
            Name of the action.
        icon_name : `str`
            Name of the icon. Must be configured in get_icon function first.
        status_tip : `str`
            Description of the action.
        icon_visible : `bool`
            Control visibility of the icon.
        connection : `function wrapper type`
            Function method to be passed as action is triggered.
        shortcut : `QShortcut`, optional
            Key shortcut for action trigger. Default is none.
        """
        action = QAction(get_icon(icon_name), caption, self)
        action.setStatusTip(status_tip)
        action.triggered.connect(connection)
        action.setIconVisibleInMenu(icon_visible)
        if shortcut is not None:
            action.setShortcuts(shortcut)
        self.addAction(action)
        return action

    @pyqtSlot(str, QWidget)
    def add_dock(self, name, widget, area=Qt.DockWidgetArea.BottomDockWidgetArea,
                 allowed_areas=Qt.DockWidgetArea.AllDockWidgetAreas, features=None, delete_on_close=True,
                 is_hidden=False, tabify=True):
        """
        Returns QDockWidget object with the set dock widget features and docking area.

        Parameters
        ----------
        name : `str`
            Name of the dock.
        widget : `QWidget`
            Widget of the dock.
        area : `QDockWidgetArea`, optional
            Docking area. Default is Qt.BottomDockWidgetArea.
        allowed_areas : `QDockWidgetArea`, optional
            Allowed docking areas in the main window. Default is Qt.AllDockWidgetAreas.
        features : `QDockWidgetFeature`, optional
            Features of the dock widget. Default is QDockWidget.AllDockWidgetFeatures.
        delete_on_close : `bool`, optional
            Deletes dock object reference upon closing.Should only be set to False for single-instance docks.
            Default is True.
        is_hidden : `bool`, optional
            Hides dock on creation if set to True. Default is False.
        tabify : `bool`, optional
            Tabifies dock with the main dock. Default is True.

        Returns
        -------
        `QDockWidget`
            QDockWidget object.
        """

        dock_widget = DockWidget(name, widget, allowed_areas, features, delete_on_close, is_hidden)
        self.addDockWidget(area, dock_widget)
        if tabify:
            self.tabifyDockWidget(self._main_dock_widget, dock_widget)
            dock_widget.show()
            dock_widget.raise_()

        return dock_widget

    def init_ribbon(self):
        """
        This initialized application ribbon bar and instantiates buttons associated with it.
        """
        portfolio_tab = self._ribbon.add_ribbon_tab("Portfolio")
        selection_pane = portfolio_tab.add_ribbon_pane("Portfolio Selection")
        selection_pane.add_ribbon_widget(RibbonButton(self, self._portfolio_tree_action, True))
        selection_pane.add_ribbon_widget(RibbonButton(self, self._create_portfolio_action, True))
        selection_pane.add_ribbon_widget(RibbonButton(self, self._delete_portfolio_action, True))

        initialization_pane = portfolio_tab.add_ribbon_pane("Initialize Portfolio")
        initialization_pane.add_ribbon_widget(RibbonButton(self, self._load_portfolio_action, True))
        grid = initialization_pane.add_grid_widget(300)
        grid.addWidget(QLabel("Portfolio:"), 1, 1)
        grid.addWidget(QLabel("Benchmark:"), 2, 1)
        grid.addWidget(QLabel("As Of Date:"), 3, 1)
        grid.addWidget(self._ptf_dropdown, 1, 2)
        grid.addWidget(self._bmk_dropdown, 2, 2)
        grid.addWidget(self._calendar, 3, 2)

        trading_pane = portfolio_tab.add_ribbon_pane("Trade")
        trading_pane.add_ribbon_widget(RibbonButton(self, self._new_trade_action, True))
        trading_pane.add_ribbon_widget(RibbonButton(self, self._delete_trade_action, True))
        trading_pane.add_ribbon_widget(RibbonButton(self, self._import_trades_action, True))
        trading_pane.add_ribbon_widget(RibbonButton(self, self._export_trades_action, True))

        subs_and_reds_pane = portfolio_tab.add_ribbon_pane("Portfolio Funds")
        subs_and_reds_pane.add_ribbon_widget(RibbonButton(self, self._subscribe_funds_action, True))
        subs_and_reds_pane.add_ribbon_widget(RibbonButton(self, self._withdraw_funds_action, True))

        portfolio_tab.add_spacer()

        backtest_tab = self._ribbon.add_ribbon_tab("Strategy Backtesting")
        timeseries_tab = self._ribbon.add_ribbon_tab("Time Series Analysis")

    def closeEvent(self, event):
        """
        Overrides default close application behavior by adding confirmation box.

        Parameters
        ----------
        event : `QCloseEvent`
            Application close event.
        """
        reply = QMessageBox.question(self, 'Message',
                                     "Quit application?", QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def on_open_portfolio_tree(self):
        """
        This method controls visibility of the portfolio tree widget.
        """
        if self._portfolio_tree_widget.isHidden():
            self._portfolio_tree_widget.setVisible(True)
        else:
            self._portfolio_tree_widget.setVisible(False)

    def on_create_new_portfolio(self):
        """
        This method opens a "Create a New Portfolio" dialog box and adds created entry to the portfolio tree view
        widget.
        """
        dlg = CreatePortfolio(self, portfolios_list=self._portfolio_tree.list_portfolios())
        if dlg.exec():
            self._portfolio_tree.add_portfolio(dlg.get_ptf_name, dlg.get_ptf_cash, dlg.get_ptf_date,
                                               dlg.get_ptf_curr)
            self._ptf_dropdown.addItem(dlg.get_ptf_name)

    def on_create_new_trade(self):
        """
        This method opens a new "Create a New Trade" dialog box. Portfolio dropdown will default to the currently
        opened portfolio and the added trade will appear in the trade table of the selected portfolio.
        """
        dlg = NewTrade(self, portfolios_list=self._portfolio_tree.list_portfolios())
        dlg.ptf_list_dropdown.setCurrentIndex(self._ptf_dropdown.currentIndex())
        if dlg.exec():
            ptf_name = dlg.get_ptf_name
            symbol = dlg.get_symbol
            quantity = dlg.get_quantity
            price = dlg.get_price
            trans_date = dlg.get_date
            comm = dlg.get_commission
            try:
                ptf = self.findChild(PortfolioWidget, ptf_name)
                ptf.insert_transaction_row([symbol, quantity, price, trans_date, comm])
            except Exception as e:
                print(e)

    def on_create_funds_transaction(self, transaction):
        dlg = NewSubRed(self, portfolios_list=self._portfolio_tree.list_portfolios(), transaction=transaction)
        dlg.ptf_list_dropdown.setCurrentIndex(self._ptf_dropdown.currentIndex())
        if dlg.exec():
            ptf_name = dlg.get_ptf_name
            symbol = dlg.get_transaction
            quantity = dlg.get_amount
            price = 0.0
            trans_date = dlg.get_date
            comm = 0.0
            try:
                ptf = self.findChild(PortfolioWidget, ptf_name)
                ptf.insert_transaction_row([symbol, quantity, price, trans_date, comm])
            except Exception as e:
                print(e)

    def on_delete_trade(self):
        """
        This method deletes a selected trade from a trade table in the selected portfolio window.
        """
        ptf_name = self._ptf_dropdown.currentText()
        try:
            ptf = self.findChild(PortfolioWidget, ptf_name)
            ptf.delete_transaction_row()
        except Exception as e:
            print(e)

    def on_import_trade_file(self):
        """
        This method opens a file dialog to import trade file. Must be a .csv file and headers must be identical
        to the table headers. File will be imported to the currently selected portfolio.
        """
        ptf_name = self._ptf_dropdown.currentText()
        dlg = QFileDialog()
        options = QFileDialog.Option.DontUseNativeDialog
        file_types = 'Comma Delimited Files (*.csv)'
        file_name, file_type = dlg.getOpenFileName(
            parent=self,
            caption='Select a file containing transaction data',
            directory='.',
            filter=file_types,
            options=options
        )
        try:
            if file_name == '':
                pass
            else:
                ptf = self.findChild(PortfolioWidget, ptf_name)
                ptf.import_trade_file_dataframe(file_name)
        except Exception as e:
            print(e)

    def on_export_trade_file(self):
        """
        This method exports trade table dataframe to a .csv file from the currently selected portfolio.
        """
        ptf_name = self._ptf_dropdown.currentText()
        dlg = QFileDialog()
        options = QFileDialog.Option.DontUseNativeDialog
        file_types = 'Comma Delimited Files (*.csv)'
        file_name, file_type = dlg.getSaveFileName(
            parent=self,
            caption='Save transaction data',
            directory='.',
            filter=file_types,
            options=options
        )
        try:
            if file_name == '':
                pass
            else:
                ptf = self.findChild(PortfolioWidget, ptf_name)
                ptf.export_trade_file_dataframe(file_name)
        except Exception as e:
            print(e)

    def on_delete_portfolio(self):
        """
        This method defines portfolio delete event when 'Delete portfolio' button is pressed. Upon clicking,
        confirmation box will pop up and once accepted selected portfolio will be deleted from the portfolio list,
        removed from the combo box and will be closed if it was open.
        """
        try:
            self._portfolio_tree.delete_portfolio()
            self._ptf_dropdown.delete_item(self._portfolio_tree.deleted_ptf)
            if self.findChild(DockWidget, self._portfolio_tree.deleted_ptf):
                self.findChild(DockWidget, self._portfolio_tree.deleted_ptf).close()
        except Exception as e:
            print(e)

    def on_portfolio_list_doubleclick(self, index):
        """
        This method defines double click event on portfolio list item. Double-clicking on an item will open a new
        portfolio dock widget.

        Parameters
        ----------
        index : `QModelIndex`
            Index of a portfolio view item.
        """
        ptf_name = index.data(Qt.ItemDataRole.UserRole)
        ptf_cash = index.data(Qt.ItemDataRole.UserRole + 1)
        ptf_start = index.data(Qt.ItemDataRole.UserRole + 2)
        ptf_curr = index.data(Qt.ItemDataRole.UserRole + 3)
        self._ptf_dropdown.setCurrentText(ptf_name)
        if self.findChild(DockWidget, ptf_name) is None:
            add_new_ptf = PortfolioWidget(ptf_name, ptf_cash, ptf_start, ptf_curr)
            self.add_dock(ptf_name, add_new_ptf)
        else:
            self.findChild(DockWidget, ptf_name).raise_()

    def on_ptf_dropdown_selection(self, selection):
        """
        This method connects to the open portfolio dock widget and raises it when the selection in portfolio
        dropdown box is made.

        Parameters
        ----------
        selection : `str`
            Ptf name in the dropdown menu.
        """
        if self.findChild(DockWidget, selection):
            self.findChild(DockWidget, selection).raise_()

    def on_docked_tab_click(self, dock):
        """
        This method is called when the tabified dock is clicked on. It updates portfolio list dropdown menu with the
        selected dock object name (Portfolio name).

        Parameters
        ----------
        dock : `QDockWidget`
            Dockwidget object.
        """
        self._ptf_dropdown.setCurrentText(dock.objectName())

    def on_load_portfolio(self):
        """
        This slot is called when load portfolio button is clicked. It computes all selected portfolio holdings and
        statistics based on the trade information available for that portfolio.
        """
        ptf_name = self._ptf_dropdown.currentText()
        bmk_name = self._bmk_dropdown.currentText()
        calculation_date = pd.to_datetime(self._calendar.text(), dayfirst=True)
        ptf = self.findChild(PortfolioWidget, ptf_name)
        ptf.update_positions_table(calculation_date, bmk_name)

    def placeholder(self):
        pass
