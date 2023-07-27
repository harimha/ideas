import fdata.api as api
from pandas.api.types import is_list_like
import plotly.graph_objects as go
from datetime import datetime
from abc import ABC, abstractmethod
from analysis.visualization import visualize
import pandas as pd


# input : raw data
# df_raw = test_rawdata()

# process
# strtg = BollingerBand(df_raw, df_raw.columns)
# df_algo = strtg.execute_algorithm(*args, **kwargs)
# df_back = strtg.backtest(df_algo)
# df_score = strtg.score(df_back)
# strtg.vis_algo
# strtg.vis_back
# strtg.vis_score


class Indicators():

    @staticmethod
    def bollinger_band(df_raw, windows=20, upper_k=2, lower_k=2):
        df_indi = df_raw.copy()
        mean = df_indi["value"].rolling(windows).mean()
        std = df_indi["value"].rolling(windows).std()
        df_indi["mid"] = mean
        df_indi["upper"] = mean + upper_k * std
        df_indi["lower"] = mean - lower_k * std

        return df_indi

    @staticmethod
    def sma(df_raw, windows: str or list):
        df_indi = df_raw.copy()
        if is_list_like(windows):
            for window in windows:
                df_indi[f"sma{window}"] = df_indi["value"].rolling(window).mean()
        else:
            df_indi[f"sma{windows}"] = df_indi["value"].rolling(windows).mean()

        return df_indi

    @staticmethod
    def visualize_indicator(indicator, *args, **kwargs):
        df_indi = indicator(*args, **kwargs)
        visualize(df_indi, df_indi.columns, name="test")


class Algorithm(ABC):

    @abstractmethod
    def _set_sub_indicators(self, *args, **kwargs):
        pass

    @abstractmethod
    def _entry_buy_condition(self, df_indi):
        cond = None

        return cond

    @abstractmethod
    def _entry_sell_condition(self, df_indi):
        cond = None

        return cond

    @abstractmethod
    def _exit_buy_condition(self, df_indi):
        cond = None

        return cond

    @abstractmethod
    def _exit_sell_condition(self, df_indi):
        cond = None

        return cond

    def _set_condition(self, df_indi):
        df_indi["entry_buy_cond"] = self._entry_buy_condition(df_indi)
        df_indi["entry_sell_cond"] = self._entry_sell_condition(df_indi)
        df_indi["exit_buy_cond"] = self._exit_buy_condition(df_indi)
        df_indi["exit_sell_cond"] = self._exit_sell_condition(df_indi)
        df_cond = df_indi

        return df_cond

    def _set_position(self, df_cond):
        df_position = df_cond
        positions = []
        pos = "nothing"
        for i in range(len(df_position)):
            if pos == "nothing":
                if df_position.iloc[i]["entry_buy_cond"]:
                    pos = "long"
                elif df_position.iloc[i]["entry_sell_cond"]:
                    pos = "short"
            elif pos == "long":
                if df_position.iloc[i]["exit_buy_cond"]:
                    pos = "nothing"
                if df_position.iloc[i]["entry_sell_cond"]:
                    pos = "short"
            elif pos == "short":
                if df_position.iloc[i]["exit_sell_cond"]:
                    pos = "nothing"
                if df_position.iloc[i]["entry_buy_cond"]:
                    pos = "long"
            positions.append(pos)
        df_position["position"] = positions

        return df_position

    def _set_signals(self, df_position):
        df_signal= df_position
        pos_now = df_signal["position"]
        pos_bef = df_signal["position"].shift(1)
        df_signal["entry_buy"] = ((pos_now == "long") & ((pos_bef == "nothing") | (pos_bef == "short")))
        df_signal["entry_sell"] = ((pos_now == "short") & ((pos_bef == "nothing") | (pos_bef == "long")))
        df_signal["exit_buy"] = (((pos_now == "nothing") | (pos_now == "short")) & ((pos_bef == "long")))
        df_signal["exit_sell"] = (((pos_now == "nothing") | (pos_now == "long")) & ((pos_bef == "short")))

        return df_signal

    def _vis_trading_signal(self, fig, df_algo):
        for i in range(len(df_algo)):
            date = df_algo.index[i]
            value = df_algo.iloc[i]["value"]
            if df_algo.iloc[i]["exit_buy"]:
                fig.add_annotation(x=date,
                                   y=value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="orange",
                                   ax=0,
                                   ay=-25,
                                   arrowwidth=1.5)
            if df_algo.iloc[i]["exit_sell"]:
                fig.add_annotation(x=date,
                                   y=value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="purple",
                                   ax=0,
                                   ay=25,
                                   arrowwidth=1.5)
            if df_algo.iloc[i]["entry_buy"]:
                fig.add_annotation(x=date,
                                   y=value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="red",
                                   ax=0,
                                   ay=25,
                                   arrowwidth=1.5)
            if df_algo.iloc[i]["entry_sell"]:
                fig.add_annotation(x=date,
                                   y=value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="blue",
                                   ax=0,
                                   ay=-25,
                                   arrowwidth=1.5)

    def execute_algorithm(self, *args, **kwargs):
        df_indi = self._set_sub_indicators(*args, **kwargs)
        df_cond = self._set_condition(df_indi)
        df_position = self._set_position(df_cond)
        df_algo = self._set_signals(df_position)

        return df_algo

    def visualize_algo(self, html=True, *args, **kwargs):
        df_algo = self.execute_algorithm(*args, **kwargs)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_algo.index,
                                 y=df_algo["value"],
                                 mode="markers",
                                 marker={"size": 3, "opacity": 0.5}))
        fig.add_trace(go.Scatter(x=df_algo[df_algo["position"] == "long"].index,
                                 y=df_algo[df_algo["position"] == "long"]["value"],
                                 mode="markers",
                                 name="long",
                                 marker={"size": 3, "opacity": 0.5}))
        fig.add_trace(go.Scatter(x=df_algo[df_algo["position"] == "short"].index,
                                 y=df_algo[df_algo["position"] == "short"]["value"],
                                 mode="markers",
                                 name="short",
                                 marker={"size": 3, "opacity": 0.5}))
        self._vis_trading_signal(fig, df_algo)

        if html:
            now = datetime.now().strftime("%Y%m%d%H%M%S")
            fig.write_html(f"{now}.html")
        else:
            fig.show()



class Backtest():
    def _set_cost(self, tax=0.002, sell_fee=0.00015, buy_fee=0.00015, slippage=0):
        sell_cost = tax+sell_fee+slippage
        buy_cost = buy_fee+slippage

        return sell_cost, buy_cost

    def _register_entry(self, trading_log, position, date, value):
        trading_log["position"].append(position)
        trading_log["entry_date"].append(date)
        trading_log["entry_value"].append(value)

    def _register_exit(self, trading_log, date, value):
        trading_log["exit_date"].append(date)
        trading_log["exit_value"].append(value)

    def backtest(self, df_algo, side="long"):
        trading_log = {"position": [], "entry_date": [], "entry_value": [],
                       "exit_date": [], "exit_value": []}
        is_long_position = False
        is_sell_position = False
        for i in range(len(df_algo)):
            date = df_algo.index[i]
            value = df_algo.iloc[i]["value"]
            position = df_algo.iloc[i]["position"]
            entry_buy_cond = ((position == "long") & (df_algo.iloc[i]["entry_buy"]))
            entry_sell_cond = ((position == "short") & (df_algo.iloc[i]["entry_sell"]))
            exit_buy_cond = (((position == "nothing") | (position == "short")) & (df_algo.iloc[i]["exit_buy"]))
            exit_sell_cond = (((position == "nothing") | (position == "long")) & (df_algo.iloc[i]["exit_sell"]))

            if entry_buy_cond:
                self._register_entry(trading_log, position, date, value)
                is_long_position = True
            if entry_sell_cond:
                self._register_entry(trading_log, position, date, value)
                is_sell_position = True
            if exit_buy_cond:
                if is_long_position:
                    self._register_exit(trading_log, date, value)
                    is_long_position = False
                else:
                    pass
            if exit_sell_cond:
                if is_sell_position:
                    self._register_exit(trading_log, date, value)
                    is_sell_position = False
                else:
                    pass

        if df_algo.iloc[-1]["position"] != "nothing":
            self._register_exit(trading_log, df_algo.index[-1], df_algo.iloc[-1]["value"])

        df_backtest = pd.DataFrame(trading_log)
        if side == "all":
            pass
        else:
            df_backtest = df_backtest.loc[df_backtest["position"] == side]
            df_backtest.index = range(len(df_backtest))

        return df_backtest

    def performance(self):
        pass

    def visualize_backtest(self):
        pass


class Strategy(Algorithm, Backtest):
    def __init__(self, df_raw=None, column=None):
        if (df_raw is None) & (column is None):
            self.df_raw = self._set_rawdata(api.stock_c("삼성전자", "20200101", "20230101"), "삼성전자")
            self.column = "삼성전자"
        else:
            self.df_raw = self._set_rawdata(df_raw, column)
            self.column = column

    def _set_rawdata(self, df_raw, column):
        raw_data = df_raw[[column]].copy()
        raw_data.columns = ["value"]

        return raw_data

class BollingerBand(Strategy):
    def __init__(self, df_raw=None, column=None):
        super().__init__(df_raw, column)

    def _set_sub_indicators(self, windows=20, upper_k=2, lower_k=2):
        df_indi = Indicators().bollinger_band(self.df_raw, windows, upper_k, lower_k)
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

    def execute_algorithm(self, windows=20, upper_k=2, lower_k=2):
        df_algo = super().execute_algorithm(windows, upper_k, lower_k)

        return df_algo

    def visualize_algo(self, windows=20, upper_k=2, lower_k=2):
        super().visualize_algo(windows=20, upper_k=2, lower_k=2)


