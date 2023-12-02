import yfinance as yf
import pandas as pd
from Infrastructure.Utilities.business_day_check import BDay

# 2LX41QJP5T79I4MF - Alpha vantage API key


class PriceDataSource:
    def __init__(self, trade_dataframe, as_of_date):
        self.trade_dataframe = trade_dataframe
        self.as_of_date = as_of_date
        self.history = self.get_price_history()

    def get_price_history(self, adjusted=True):
        tickers = self.trade_dataframe["Symbol"].unique()
        tickers = [ticker for ticker in tickers.tolist() if ticker not in ('SUBSCRIPTION', 'WITHDRAWAL')]
        start_date = self.trade_dataframe["Date"].min()
        start_date = start_date.strftime("%Y-%m-%d")
        prices = yf.download(tickers, start=start_date, end=self.as_of_date + BDay(1))

        if adjusted:
            return prices["Adj Close"]
        else:
            return prices["Close"]

    def get_price_from_history(self, ticker, date):
        if isinstance(self.history, pd.Series):
            return self.history.loc[date]
        return self.history.loc[date][ticker]
