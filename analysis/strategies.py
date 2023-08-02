from analysis.base import Algorithm, Backtest, Visualize
from analysis.indicator import sma, bollinger_band, up_trend, macd
import fdata.api as api
import numpy as np


class Strategy(Algorithm, Backtest, Visualize):
    def __init__(self, df_raw=None, column=None, **params):
        if (df_raw is None) & (column is None):
            self.df_raw = self._set_rawdata(api.stock_c("삼성전자", "20200101", "20230101"), "삼성전자")
            self.column = "삼성전자"
        else:
            self.df_raw = self._set_rawdata(df_raw, column)
            self.column = column
        self.set_params(**params)
        super().__init__()

    def _set_rawdata(self, df_raw, column):
        raw_data = df_raw[[column]].copy()
        raw_data.columns = ["value"]

        return raw_data

    def set_params(self, **params):
        self.params = params

    def backtest(self, side="long"):
        df_algo = self.execute_algorithm()
        df_backtest = super().backtest(df_algo, side)

        return df_backtest


class BollingerBand(Strategy):
    def __init__(self, df_raw=None, column=None, windows=20, upper_k=2, lower_k=2):
        super().__init__(df_raw, column, windows=windows, upper_k=upper_k, lower_k=lower_k)

    def set_params(self, windows, upper_k, lower_k):
        super().set_params(windows=windows, upper_k=upper_k, lower_k=lower_k)

    def set_sub_indicators(self):
        df_indi = bollinger_band(self.df_raw, self.column, **self.params)
        df_indi.dropna(inplace=True)

        return df_indi

    def _entry_buy_condition(self, df_indi):
        cond = df_indi["value"] >= df_indi["upper"]

        return cond

    def _entry_sell_condition(self, df_indi):
        cond = df_indi["value"] <= df_indi["lower"]

        return cond

    def _exit_buy_condition(self, df_indi):
        cond = df_indi["value"] <= df_indi["mid"]

        return cond

    def _exit_sell_condition(self, df_indi):
        cond = df_indi["value"] > df_indi["mid"]

        return cond


class GoldenDeadCross(Strategy):
    def __init__(self, df_raw=None, column=None, short=20, long=60):
        super().__init__(df_raw, column, short=short, long=long)

    def set_params(self, short, long):
        super().set_params(short=short, long=long)

    def set_sub_indicators(self):
        df_indi = sma(self.df_raw, self.column, *self.params.values())
        df_indi.dropna(inplace=True)

        return df_indi

    def _entry_buy_condition(self, df_indi):
        cond = df_indi[f"sma{self.params['short']}"] >= df_indi[f"sma{self.params['long']}"]

        return cond

    def _entry_sell_condition(self, df_indi):
        cond = df_indi[f"sma{self.params['short']}"] < df_indi[f"sma{self.params['long']}"]

        return cond

    def _exit_buy_condition(self, df_indi):
        cond = df_indi[f"sma{self.params['short']}"] < df_indi[f"sma{self.params['long']}"]

        return cond

    def _exit_sell_condition(self, df_indi):
        cond = df_indi[f"sma{self.params['short']}"] >= df_indi[f"sma{self.params['long']}"]

        return cond


class UpTrend(Strategy):
    def __init__(self, df_raw=None, column=None, rate=1.005):
        super().__init__(df_raw, column, rate=rate)

    def set_params(self, rate):
        super().set_params(rate=rate)

    def set_sub_indicators(self):
        df_indi = up_trend(self.df_raw, self.column, *self.params.values())

        count = 0
        counts = []
        for i in range(len(df_indi)):
            if df_indi["indi2"].iloc[i]:
                count += 1
            else:
                count = 0
            counts.append(count)
        df_indi["count"] = counts

        up = []
        for i in range(len(df_indi)):
            up.append(False)
            if df_indi.iloc[i]["count"] >= 10:
                up[i - 10:] = [True] * 11
        df_indi["up"] = up
        df_indi=df_indi[["value","indi","up"]]

        return df_indi

    def _entry_buy_condition(self, df_indi):
        cond = df_indi["up"]

        return cond

    def _entry_sell_condition(self, df_indi):
        cond = df_indi["up"]==False

        return cond

    def _exit_buy_condition(self, df_indi):
        cond = df_indi["up"]==False

        return cond

    def _exit_sell_condition(self, df_indi):
        cond = df_indi["up"]

        return cond


class MACD(Strategy):
    def __init__(self, df_raw=None, column=None, short=20, long=60, ima=9, ema=True):
        super().__init__(df_raw, column, short=short, long=long, ima=ima, ema=ema)

    def set_params(self, short, long, ima, ema):
        '''
        이후 파라미터 변경시 활용하는 용도
        '''
        super().set_params(short=short, long=long, ima=ima, ema=ema)

    def set_sub_indicators(self):
        df_indi = macd(np.log(self.df_raw), self.column, **self.params)
        df_indi = df_indi[["value", f"macd_{self.params['short']}_{self.params['long']}", "ima_9"]]
        df_indi["value"] = self.df_raw["value"]
        df_indi.dropna(inplace=True)

        return df_indi


    def _entry_buy_condition(self, df_indi):

        cond1 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"] >= df_indi["ima_9"]
        cond2 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1) < df_indi["ima_9"].shift(1)
        cond3 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1)<=-0.1
        cond = cond1 & cond2 & cond3

        return cond

    def _entry_sell_condition(self, df_indi):
        cond1 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"] <= df_indi["ima_9"]
        cond2 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1) > df_indi["ima_9"].shift(1)
        cond3 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1)>=0.1
        cond = cond1 & cond2 & cond3
        return cond

    def _exit_buy_condition(self, df_indi):
        cond1 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"] <= df_indi["ima_9"]
        cond2 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1) > df_indi["ima_9"].shift(1)
        cond3 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1) >= 0.1
        cond = cond1 & cond2 & cond3
        return cond

    def _exit_sell_condition(self, df_indi):
        cond1 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"] >= df_indi["ima_9"]
        cond2 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1) < df_indi["ima_9"].shift(1)
        cond3 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1) <= -0.1
        cond = cond1 & cond2 & cond3
        return cond