import pandas as pd
import fdata.api as api
from analysis.mixin import Strategy
from analysis.indicator import sma


class BollingerBand(Strategy):
    def __init__(self, df, column):
        super().__init__(df, column)

    def _set_sub_indicators(self):
        self.data["midline"] = self.data[self.column].rolling(20).mean()
        self.data["upper_bound"] = \
            self.data[self.column].rolling(20).mean() + 2 * self.data[self.column].rolling(20).std()
        self.data["lower_bound"] = \
            self.data[self.column].rolling(20).mean() - 2 * self.data[self.column].rolling(20).std()
        self.data.dropna(inplace=True)

    def _set_algorithm(self):
        self.data["entry_buy_cond"] = self.data[self.column] >= self.data["upper_bound"]
        self.data["entry_sell_cond"] = self.data[self.column] <= self.data["lower_bound"]
        self.data["exit_buy_cond"] = self.data[self.column] <= self.data["midline"]
        self.data["exit_sell_cond"] = self.data[self.column] > self.data["midline"]

class GoldenDeadCross(Strategy):
    def __init__(self, df, column, short, long):
        self.short = short
        self.long = long
        super().__init__(df, column)

    def _set_sub_indicators(self):
        self.data = sma(self.data, self.column, [self.short, self.long])
        self.data.dropna(inplace=True)

    def _set_algorithm(self):
        self.data["entry_buy_cond"] = \
            (self.data[f"{self.column}_sma{self.short}"] >= self.data[f"{self.column}_sma{self.long}"])
        self.data["entry_sell_cond"] = \
            (self.data[f"{self.column}_sma{self.short}"] < self.data[f"{self.column}_sma{self.long}"])
        self.data["exit_buy_cond"] = \
            (self.data[f"{self.column}_sma{self.short}"] < self.data[f"{self.column}_sma{self.long}"])
        self.data["exit_sell_cond"] = \
            (self.data[f"{self.column}_sma{self.short}"] >= self.data[f"{self.column}_sma{self.long}"])


df = api.stock_c("삼성전자", "20010101", "20050101")
gdc = GoldenDeadCross(df, "삼성전자", 20, 60)
gdc = BollingerBand(df, "삼성전자")
gdc.backtest()
gdc.trading_log
gdc.visualize_1(False)
