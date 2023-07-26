import pandas as pd
import fdata.api as api
from analysis.mixin import Strategy
from analysis.indicator import sma
from analysis.utils import Singleton


class BollingerBand(Strategy):
    def __init__(self, df, column):
        super().__init__(df, column)

    def _set_sub_indicators(self):
        self.data["midline"] = self.data[self.column].rolling(20).mean()
        self.data["upper_bound"] = \
            self.data[self.column].rolling(20).mean() + 2 * self.data[self.column].rolling(20).std()
        self.data["lower_bound"] = \
            self.data[self.column].rolling(20).mean() - 2 * self.data[self.column].rolling(20).std()

    def _entry_buy_condition(self):
        cond = self.data[self.column] >= self.data["upper_bound"]

        return cond

    def _entry_sell_condition(self):
        cond = self.data[self.column] <= self.data["lower_bound"]

        return cond

    def _exit_buy_condition(self):
        cond = self.data[self.column] <= self.data["midline"]

        return cond

    def _exit_sell_condition(self):
        cond = self.data[self.column] > self.data["midline"]

        return cond


class GoldenDeadCross(Strategy):
    def __init__(self, df, column, short, long):
        self.short = short
        self.long = long
        super().__init__(df, column)

    def _set_sub_indicators(self):
        self.data = sma(self.data, self.column, [self.short, self.long])

    def _entry_buy_condition(self):
        cond = self.data[f"{self.column}_sma{self.short}"] >= self.data[f"{self.column}_sma{self.long}"]
        return cond

    def _entry_sell_condition(self):
        cond = self.data[f"{self.column}_sma{self.short}"] < self.data[f"{self.column}_sma{self.long}"]
        return cond

    def _exit_buy_condition(self):
        cond = self.data[f"{self.column}_sma{self.short}"] < self.data[f"{self.column}_sma{self.long}"]
        return cond

    def _exit_sell_condition(self):
        cond = self.data[f"{self.column}_sma{self.short}"] >= self.data[f"{self.column}_sma{self.long}"]
        return cond



class Mix1(GoldenDeadCross, BollingerBand):
    def __init__(self, df, column, short, long):
        GoldenDeadCross.__init__(self, df, column, short, long)

    def _set_sub_indicators(self):
        GoldenDeadCross._set_sub_indicators(self)
        BollingerBand._set_sub_indicators(self)
    def _entry_buy_condition(self):
        cond =BollingerBand._entry_buy_condition(self)
        return cond
    def _entry_sell_condition(self):
        cond = BollingerBand._entry_sell_condition(self)
        return cond
    def _exit_buy_condition(self):
        cond = GoldenDeadCross._exit_buy_condition(self)
        return cond
    def _exit_sell_condition(self):
        cond = GoldenDeadCross._exit_sell_condition(self)
        return cond



    
    

# 2개 이상의 지표 겹쳐보기
# entry area, exit area 개별로 보여주고 합쳐진 entry area, exit area 보여주기

# 2개 이상의 지표 합치기

df = api.stock_c("삼성전자", "20010101", "20050101")
m = Mix1(df, "삼성전자", 20, 60)
m.visualize_algo()
m.data.head()
#
# m.data.head()
# m.backtest()
# m.trading_log
# m.visualize_1(True)
#
# gdc = GoldenDeadCross(df, "삼성전자", 20, 60)
# bb = BollingerBand(df, "삼성전자")
# gdc.execute_algo()
# bb.execute_algo()
# gdc.backtest()
#
# bb.backtest()
# gdc.visualize_1()
# bb.visualize_1()
