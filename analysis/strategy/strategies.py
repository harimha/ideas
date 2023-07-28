from analysis.strategy.base import Algorithm, Backtest, Visualize
from analysis.strategy.indicator import Indicator
import fdata.api as api


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
        df_indi = Indicator().bollinger_band(self.df_raw, **self.params)
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
    pass


bb = BollingerBand()
df_indi = bb.set_sub_indicators()
df_algo = bb.execute_algorithm()
df_backtest = bb.backtest()


# from datetime import datetime
fig = bb.init_fig()
# fig = bb.vis_backtest(fig, df_indi, df_backtest)
fig = bb.vis_entry_exit(fig, df_indi, df_algo)
# fig = bb.change_layout_color(fig, (df_indi.index[10],df_indi.index[10]), "lightgray")

bb.fig_show(fig)
