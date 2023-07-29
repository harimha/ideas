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
    def __init__(self, df_raw=None, column=None, short=20, long=60):
        super().__init__(df_raw, column, short=short, long=long)

    def set_params(self, short, long):
        super().set_params(short=short, long=long)

    def set_sub_indicators(self):
        df_indi = Indicator().sma(self.df_raw, *self.params.values())
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


bb = BollingerBand()
gd = GoldenDeadCross()
# df_indi = bb.set_sub_indicators()
# df_cond = bb.get_condition_df(df_indi)
# df_position = bb.get_position_df(df_cond)
# df_sig = bb.get_trading_signal_df(df_position)
# df_algo = bb.execute_algorithm()
# df_backtest = bb.backtest()

df_indi = gd.set_sub_indicators()
df_cond = gd.get_condition_df(df_indi)
df_position = gd.get_position_df(df_cond)
df_sig = gd.get_trading_signal_df(df_position)
df_algo = gd.execute_algorithm()
df_backtest = gd.backtest()
#
# fig = bb.init_fig(secondary_y=False)
# fig = bb.vis_algo(fig, df_algo, vis_indi=False)
# bb.fig_show(fig, html=False)
fig = gd.init_fig(2,1)
# gd.add_secondary_y(fig,2,1)

fig = gd.vis_value(fig, df_indi["value"], 2,1)
fig = gd.vis_sub_indicator(fig, df_indi, 1,1)


# fig = gd.vis_backtest(fig, df_algo, df_backtest, vis_indi=True, secondary_y=True)

# gd.update_secondary_y(fig, row=1, col=1, secondary_y=False)
gd.fig_show(fig, html=False)