from analysis.indicator import sma
from pandas.api.types import is_list_like
import fdata.api as api


class Strategy():
    def __init__(self):
        pass

    def golden_dead_cross(self, data, columns, short: int, long: int):
        counts = len(columns)
        if is_list_like(columns):
            df = sma(data, columns, [short, long])
            df = df.dropna()
            for col in columns:
                golden = df[f"{col}_sma{short}"] >= df[f"{col}_sma{long}"]
                df.loc[golden, f"{col}_state"] = 1
                df = df.fillna(0)
                buy_sig = ((df[f"{col}_state"] == 1) & (df[f"{col}_state"].shift(1) == 0))
                sell_sig = ((df[f"{col}_state"] == 0) & (df[f"{col}_state"].shift(1) == 1))
                df.loc[buy_sig, f"{col}_signal"] = "buy"
                df.loc[sell_sig, f"{col}_signal"] = "sell"
                df = df.fillna("hold")
        else:
            df = sma(data, columns, [short, long])
            df = df.dropna()
            golden = df[f"{columns}_sma{short}"] >= df[f"{columns}_sma{long}"]
            df.loc[golden, f"{columns}_state"] = 1
            df = df.fillna(0)
            buy_sig = ((df[f"{columns}_state"] == 1) & (df[f"{columns}_state"].shift(1) == 0))
            sell_sig = ((df[f"{columns}_state"] == 0) & (df[f"{columns}_state"].shift(1) == 1))
            df.loc[buy_sig, f"{columns}_signal"] = "buy"
            df.loc[sell_sig, f"{columns}_signal"] = "sell"
            df = df.fillna("hold")

        return df


# def golden_dead_cross(data, columns, short:int, long:int):
#     '''
#     골든 크로스 : 단기 이평선이 장기 이평선을 상향 돌파, 매수 신호
#     데드 크로스 : 단기 이평선이 장기 이평선을 하향 돌파, 매도 신호
#     '''
#     counts = len(columns)
#     if is_list_like(columns):
#         df = sma(data, columns, [short, long])
#         df = df.dropna()
#         for col in columns:
#             golden = df[f"{col}_sma{short}"] >= df[f"{col}_sma{long}"]
#             df.loc[golden, f"{col}_state"] = 1
#             df = df.fillna(0)
#             buy_sig = ((df[f"{col}_state"] == 1) & (df[f"{col}_state"].shift(1) == 0))
#             sell_sig = ((df[f"{col}_state"] == 0) & (df[f"{col}_state"].shift(1) == 1))
#             df.loc[buy_sig, f"{col}_signal"] = "buy"
#             df.loc[sell_sig, f"{col}_signal"] = "sell"
#             df = df.fillna("hold")
#     else:
#         df = sma(data, columns, [short, long])
#         df = df.dropna()
#         golden = df[f"{columns}_sma{short}"] >= df[f"{columns}_sma{long}"]
#         df.loc[golden, f"{columns}_state"] = 1
#         df = df.fillna(0)
#         buy_sig = ((df[f"{columns}_state"] == 1) & (df[f"{columns}_state"].shift(1) == 0))
#         sell_sig = ((df[f"{columns}_state"] == 0) & (df[f"{columns}_state"].shift(1) == 1))
#         df.loc[buy_sig, f"{columns}_signal"] = "buy"
#         df.loc[sell_sig, f"{columns}_signal"] = "sell"
#         df = df.fillna("hold")
#
#     return df


class Stock(Strategy):
    def __init__(self, stock_name, sdate, edate):
        self.stock_name = stock_name
        self.sdate = sdate
        self.edate = edate
        self.df = api.stock_ohlcv(stock_name, sdate, edate)
        self.columns = self.df.columns

    def golden_dead_cross(self, short: int, long: int):
        super().golden_dead_cross()

    def backtest(self, func):
        pass

    def visualize(self, func):
        pass




class Strategy():
    def __init__(self):
        pass

class GoldenDeadCross(Strategy):
    def __init__(self, df):
        self.df = df.copy()

    def backtest(self):
        pass

    def visualize(self):
        pass

    def log(self):
        pass

