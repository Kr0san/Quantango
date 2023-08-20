import numpy as np

from Infrastructure.Portfolio.portfolio import Portfolio
from Infrastructure.Portfolio.transaction import Transaction
from Infrastructure.Utilities.business_day_check import is_business_day, BDay
from pandas_datareader import data as pdr
from Infrastructure.Utilities.data_sourcer import PriceDataSource
import pandas as pd
import yfinance as yf
import quantstats as qs
from datetime import datetime as _dt
from dateutil.relativedelta import relativedelta
from Infrastructure.Utilities.custom_statistics import omega
import empyrical as ep

yf.pdr_override()
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 400)


class PortfolioConstructor:
    def __init__(self, start_date, start_cash, ptf_name, ptf_curr):
        self.start_date = pd.to_datetime(start_date, dayfirst=True)
        self.start_cash = float(start_cash)
        self.ptf_name = ptf_name
        self.ptf_curr = ptf_curr
        self.ptf = Portfolio(self.start_date, self.start_cash, currency=self.ptf_curr, name=self.ptf_name)
        self.holdings_as_of_date = None
        self.portfolio_timeseries = None

    @property
    def portfolio(self):
        return self.ptf

    @property
    def holdings(self):
        return self.holdings_as_of_date

    def construct_positions(self, date, trade_dataframe):
        # date = pd.to_datetime(date, dayfirst=True)
        # ph = PositionHandler()
        position_info = []
        for transaction in self.construct_transactions(trade_dataframe):
            if not is_business_day(transaction.dt):
                raise ValueError(f"Transaction {transaction} must be on a business day!")
            if transaction.dt <= date:
                if transaction.asset == "SUBSCRIPTION":
                    self.portfolio.subscribe_funds(transaction.dt, transaction.quantity)
                elif transaction.asset == "WITHDRAWAL":
                    self.portfolio.withdraw_funds(transaction.dt, transaction.quantity)
                else:
                    self.portfolio.transact_asset(transaction)

        for asset in self.portfolio.pos_handler.positions.keys():
            price = self.get_current_price(asset, date)
            position = self.portfolio.pos_handler.positions[asset]
            position.update_current_price(price, date)
            position_info.append([position.asset, position.net_quantity, position.market_price, position.market_value,
                                  position.avg_price, position.net_incl_commission, position.unrealised_pnl,
                                  position.realised_pnl, position.total_pnl, position.current_dt])
        return position_info

    def construct_portfolio_history(self, trades, end_date):
        data_handler = PriceDataSource(trades, end_date)
        date_index = pd.date_range(self.start_date, end_date, freq=BDay())
        position_info = {'Symbol': [], 'Quantity': [], 'Market Price': [], 'Market Value': [], 'Avg Price': [],
                         'Total Cost': [], 'Unrealized PL': [], 'Realized PL': [], 'Total PL': [], 'Holding Date': []}

        portfolio_timeseries = {'Date': [], 'Total Equity': [], 'Total Market Value': [], 'Total RPL': [],
                                'Total UPL': [], 'Total PNL': []}

        for date in date_index:
            for transaction in self.construct_transactions(trades):
                if date == transaction.dt:
                    if transaction.asset == "SUBSCRIPTION":
                        self.portfolio.subscribe_funds(transaction.dt, transaction.quantity)
                    elif transaction.asset == "WITHDRAWAL":
                        self.portfolio.withdraw_funds(transaction.dt, transaction.quantity)
                    else:
                        self.portfolio.transact_asset(transaction)
            for asset in self.portfolio.pos_handler.positions.keys():
                try:
                    price = data_handler.get_price_from_history(asset, date)
                    position = self.portfolio.pos_handler.positions[asset]
                    position.update_current_price(price, date)
                    position_info["Symbol"].append(position.asset)
                    position_info["Quantity"].append(position.net_quantity)
                    position_info["Market Price"].append(position.market_price)
                    position_info["Market Value"].append(position.market_value)
                    position_info["Avg Price"].append(position.avg_price)
                    position_info["Total Cost"].append(position.net_incl_commission)
                    position_info["Unrealized PL"].append(position.unrealised_pnl)
                    position_info["Realized PL"].append(position.realised_pnl)
                    position_info["Total PL"].append(position.total_pnl)
                    position_info["Holding Date"].append(position.current_dt)
                except KeyError:
                    pass

            portfolio_timeseries['Date'].append(date)
            portfolio_timeseries['Total Equity'].append(self.portfolio.total_equity)
            portfolio_timeseries['Total Market Value'].append(self.portfolio.total_market_value)
            portfolio_timeseries['Total RPL'].append(self.portfolio.total_realised_pnl)
            portfolio_timeseries['Total UPL'].append(self.portfolio.total_unrealised_pnl)
            portfolio_timeseries['Total PNL'].append(self.portfolio.total_pnl)

        position_info_df = pd.DataFrame(position_info)
        self.holdings_as_of_date = position_info_df.loc[position_info_df['Holding Date'] == end_date]
        portfolio_timeseries_df = pd.DataFrame(portfolio_timeseries)
        self.portfolio_timeseries = portfolio_timeseries_df

    def construct_portfolio_returns(self):
        """
        Helper method to construct portfolio returns from the total equity.

        Returns
        -------
        `pd.DataFrame`
            Portfolio returns dataframe.
        """
        ptf_df = self.portfolio_timeseries[['Date', 'Total Equity']].copy()
        ptf_df['Ptf Returns'] = ptf_df['Total Equity'].pct_change().fillna(0.0)
        ptf_df = ptf_df.set_index('Date')

        return ptf_df

    def construct_benchmark_returns(self, benchmark, end_date):
        """
        Helper method to construct benchmark returns series.

        Parameters
        ----------
        benchmark : `str`
            Name of the benchmark. Passed from the main window dropdown.
        end_date : `pd.Timestamp`
            End date of the benchmark series.

        Returns
        -------
        `pd.DataFrame`
            Dataframe object containing benchmark returns.
        """
        bmk_name_map = {'S&P 500': '^GSPC', 'NASDAQ': '^IXIC', 'Dow Jones': '^DJI', 'Russell 2000': '^RUT',
                        'Nikkei 225': '^N225', 'Hang Seng': '^HSI', 'Euro Stoxx 50': '^STOXX50E'}
        data = pdr.get_data_yahoo(bmk_name_map[benchmark], start=self.start_date, end=end_date + BDay(1))
        # data['Bmk Returns'] = data['Close'].pct_change().fillna(0.0)
        data.rename(columns={'Adj Close': 'Benchmark'}, inplace=True)

        return data['Benchmark']

    def construct_returns_dataframe(self, benchmark, end_date):
        """
        Helper method that construct a combined dataframe containing portfolio and benchmark returns.

        Parameters
        ----------
        benchmark : `str`
            Name of the benchmark. Passed from the main window dropdown.
        end_date : `pd.Timestamp`
            End date of the benchmark series.

        Returns
        -------
        `pd.DataFrame`
            Dataframe object containing combined portfolio and benchmark returns.
        """
        ptf_returns = self.construct_portfolio_returns()
        bmk_returns = self.construct_benchmark_returns(benchmark, end_date)
        returns_df = ptf_returns.join(bmk_returns).fillna(method='ffill')
        returns_df['Bmk Returns'] = returns_df['Benchmark'].pct_change().fillna(0.0)

        return returns_df

    @staticmethod
    def construct_statistics(portfolio_returns, benchmark_returns, metrics="returns"):

        def returns_statistics(returns):

            today = returns.index[-1]
            delta_3m = today - relativedelta(months=3)
            delta_6m = today - relativedelta(months=6)
            delta_1y = today - relativedelta(years=1)

            stats = [str(np.round(qs.stats.comp(returns) * 100, 2)) + ' %',
                     str(np.round(qs.stats.cagr(returns, periods=365) * 100, 2)) + ' %',
                     str(np.round(qs.stats.expected_return(returns) * 100, 2)) + ' %',
                     str(np.round(qs.stats.expected_return(returns, aggregate="M") * 100, 2)) + ' %',
                     str(np.round(qs.stats.expected_return(returns, aggregate="A") * 100, 2)) + ' %',
                     str(np.round(qs.stats.comp(returns[returns.index >= _dt(today.year, today.month, 1)]) * 100
                                  , 2))+' %',
                     str(np.round(qs.stats.comp(returns[returns.index >= delta_3m]) * 100, 2)) + ' %',
                     str(np.round(qs.stats.comp(returns[returns.index >= delta_6m]) * 100, 2)) + ' %',
                     str(np.round(qs.stats.comp(returns[returns.index >= _dt(today.year, 1, 1)]) * 100
                                  , 2)) + ' %',
                     str(np.round(qs.stats.comp(returns[returns.index >= delta_1y]) * 100, 2)) + ' %']

            return stats

        def performance_statistics(returns, risk_free_rate=0.0, required_return=0.0):

            stats = [np.round(qs.stats.sharpe(returns, rf=risk_free_rate), 2),
                     np.round(qs.stats.sortino(returns, rf=risk_free_rate), 2),
                     np.round(ep.stats.omega_ratio(returns, risk_free=risk_free_rate, required_return=required_return)
                              , 2),
                     str(np.round(qs.stats.kelly_criterion(returns) * 100, 2)) + ' %',
                     np.round(qs.stats.payoff_ratio(returns), 2),
                     np.round(qs.stats.calmar(returns), 2),
                     np.round(qs.stats.cpc_index(returns), 2),
                     np.round(qs.stats.outlier_win_ratio(returns), 2),
                     np.round(qs.stats.outlier_loss_ratio(returns), 2),
                     np.round(qs.stats.tail_ratio(returns), 2)]

            return stats

        def risk_statistics(returns):
            drawdown = qs.stats.to_drawdown_series(returns)
            drawdown_info = qs.stats.drawdown_details(drawdown)

            max_dd = drawdown_info.sort_values(by="max drawdown", ascending=True)["max drawdown"].values[0]
            dd_days = drawdown_info.sort_values(by="days", ascending=False)["days"].values[0]
            avg_dd = drawdown_info["max drawdown"].mean()

            stats = [str(np.round(qs.stats.var(returns) * 100, 2)) + ' %',
                     str(np.round(qs.stats.cvar(returns) * 100, 2)) + ' %',
                     str(np.round(qs.stats.risk_of_ruin(returns) * 100, 2)) + ' %',
                     str(np.round(qs.stats.volatility(returns) * 100, 2)) + ' %',
                     np.round(qs.stats.skew(returns), 2),
                     np.round(qs.stats.kurtosis(returns), 2),
                     str(np.round(max_dd, 2)) + ' %',
                     int(dd_days),
                     str(np.round(avg_dd, 2)) + ' %',
                     np.round(qs.stats.recovery_factor(returns), 2)
                     ]

            return stats

        if metrics == "returns":
            ptf_metrics = returns_statistics(portfolio_returns)
            bmk_metrics = returns_statistics(benchmark_returns)

            combined_metrics = {"Portfolio": ptf_metrics, "Benchmark": bmk_metrics}
            combined_metrics_df = pd.DataFrame(data=combined_metrics,
                                               index=['Cum. Return', 'CAGR',
                                                      'Ex. Return (D)', 'Ex. Return (M)',
                                                      'Ex. Return (Y)', 'MTD Return',
                                                      '3M Return', '6M Return', 'YTD Return', '1Y Return'])

            return combined_metrics_df

        if metrics == "performance":
            ptf_metrics = performance_statistics(portfolio_returns)
            bmk_metrics = performance_statistics(benchmark_returns)

            combined_metrics = {"Portfolio": ptf_metrics, "Benchmark": bmk_metrics}
            combined_metrics_df = pd.DataFrame(data=combined_metrics,
                                               index=['Sharpe Ratio', 'Sortino Ratio',
                                                      'Omega Ratio', 'Kelly Criterion',
                                                      'Payoff Ratio', 'Calmar Ratio',
                                                      'CPC Index', 'Outlier Win',
                                                      'Outlier Loss', 'Tail Ratio'])

            return combined_metrics_df

        if metrics == "risk":
            ptf_metrics = risk_statistics(portfolio_returns)
            bmk_metrics = risk_statistics(benchmark_returns)

            combined_metrics = {"Portfolio": ptf_metrics, "Benchmark": bmk_metrics}
            combined_metrics_df = pd.DataFrame(data=combined_metrics,
                                               index=['VaR', 'cVaR', 'Risk of Ruin', 'Volatility', 'Skewness',
                                                      'Kurtosis', 'Max DD', 'DD Duration', 'Avg. DD', 'Rec. Factor'])

            return combined_metrics_df

    @staticmethod
    def construct_additional_statistics(portfolio_returns, benchmark_returns):
        # ptf_returns = self.portfolio_timeseries['Total Equity'].pct_change().fillna(0.0)
        alpha, beta = ep.alpha_beta(portfolio_returns, benchmark_returns)
        information_ratio = qs.stats.information_ratio(portfolio_returns, benchmark_returns)
        treynor_ratio = qs.stats.treynor_ratio(portfolio_returns, benchmark_returns)
        r_squared = qs.stats.r_squared(portfolio_returns, benchmark_returns)
        up_capture = ep.up_capture(portfolio_returns, benchmark_returns)
        down_capture = ep.down_capture(portfolio_returns, benchmark_returns)
        batting_ratio = ep.batting_average(portfolio_returns, benchmark_returns)["batting average"] * 100

        data = [[np.round(alpha, 2), np.round(beta, 2),
                 np.round(information_ratio, 2), np.round(treynor_ratio, 2),
                 np.round(r_squared, 2), np.round(up_capture, 2), np.round(down_capture, 2),
                 str(np.round(batting_ratio, 2)) + ' %']]

        metrics_df = pd.DataFrame(data=data, columns=['Alpha', 'Beta', 'Information Ratio', 'Treynor Ratio',
                                                      'R-Squared', 'Up Capture', 'Down Capture', 'Batting Ratio'])

        return metrics_df

    @staticmethod
    def construct_transactions(trade_dataframe):
        trades = trade_dataframe
        trades.sort_values(['Date'], inplace=True)

        trans = [Transaction(asset, quantity, dt, price, 1, commission) for asset, quantity, dt, price, commission in
                 zip(trades['Symbol'], trades['Quantity'], trades['Date'], trades['Price'], trades['Commission'])]

        return trans

    @staticmethod
    def get_current_price(ticker, date):
        data = pdr.get_data_yahoo(ticker, start=date - BDay(1), end=date)
        return data.iloc[0]['Adj Close']
