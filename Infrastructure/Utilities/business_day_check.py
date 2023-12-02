from pandas.tseries.offsets import BDay
import pandas as pd


def is_business_day(date):
    day = BDay()
    if isinstance(date, str):
        date = pd.to_datetime(date, dayfirst=False)
    business_day = day.is_on_offset(date)

    return business_day
