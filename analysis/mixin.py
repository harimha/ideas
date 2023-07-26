import datetime
from plotly.subplots import make_subplots
from abc import ABC, abstractmethod
import pandas as pd
import plotly.graph_objects as go
from analysis.utils import Singleton


class Algorithm(ABC):

    @abstractmethod
    def _set_sub_indicators(self):
        pass

    @abstractmethod
    def _entry_buy_condition(self):
        pass

    @abstractmethod
    def _entry_sell_condition(self):
        pass

    @abstractmethod
    def _exit_buy_condition(self):
        pass

    @abstractmethod
    def _exit_sell_condition(self):
        pass

    def _set_algorithm(self):
        self.data.dropna(inplace=True)
        self.data["entry_buy_cond"] = self._entry_buy_condition()
        self.data["entry_sell_cond"] = self._entry_sell_condition()
        self.data["exit_buy_cond"] = self._exit_buy_condition()
        self.data["exit_sell_cond"] = self._exit_sell_condition()

    def _set_positions(self):
        positions = []
        pos = "nothing"
        for i in range(len(self.data)):
            if pos == "nothing":
                if self.data.iloc[i]["entry_buy_cond"]:
                    pos = "long"
                elif self.data.iloc[i]["entry_sell_cond"]:
                    pos = "short"
            elif pos == "long":
                if self.data.iloc[i]["exit_buy_cond"]:
                    pos = "nothing"
                if self.data.iloc[i]["entry_sell_cond"]:
                    pos = "short"
            elif pos == "short":
                if self.data.iloc[i]["exit_sell_cond"]:
                    pos = "nothing"
                if self.data.iloc[i]["entry_buy_cond"]:
                    pos = "long"
            positions.append(pos)
        self.data = pd.DataFrame({"value":self.data[self.column],
                                  "position": positions}, index=self.data.index)

    def _set_trading_signals(self):
        pos_now = self.data["position"]
        pos_bef = self.data["position"].shift(1)
        self.data["entry_buy"] = ((pos_now == "long") & ((pos_bef == "nothing") | (pos_bef == "short")))
        self.data["entry_sell"] = ((pos_now == "short") & ((pos_bef == "nothing") | (pos_bef == "long")))
        self.data["exit_buy"] = (((pos_now == "nothing") | (pos_now == "short")) & ((pos_bef == "long")))
        self.data["exit_sell"] = (((pos_now == "nothing") | (pos_now == "long")) & ((pos_bef == "short")))

    def _vis_trading_signal(self, fig):
        for i in range(len(self.data)):
            date = self.data.index[i]
            value = self.data.iloc[i]["value"]
            if self.data.iloc[i]["exit_buy"]:
                fig.add_annotation(x=date,
                                   y=value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="orange",
                                   ax=0,
                                   ay=-25,
                                   arrowwidth=1.5)
            if self.data.iloc[i]["exit_sell"]:
                fig.add_annotation(x=date,
                                   y=value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="purple",
                                   ax=0,
                                   ay=25,
                                   arrowwidth=1.5)
            if self.data.iloc[i]["entry_buy"]:
                fig.add_annotation(x=date,
                                   y=value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="red",
                                   ax=0,
                                   ay=25,
                                   arrowwidth=1.5)
            if self.data.iloc[i]["entry_sell"]:
                fig.add_annotation(x=date,
                                   y=value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="blue",
                                   ax=0,
                                   ay=-25,
                                   arrowwidth=1.5)

    def execute_algo(self):
        self.data = self.raw_data.copy()
        self._set_sub_indicators()
        self._set_algorithm()
        self._set_positions()
        self._set_trading_signals()

    def visualize_algo(self, html=True):
        self.execute_algo()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.data.index,
                                 y=self.data["value"],
                                 mode="markers",
                                 marker={"size": 3, "opacity": 0.5}))
        fig.add_trace(go.Scatter(x=self.data[self.data["position"] == "long"].index,
                                 y=self.data[self.data["position"] == "long"]["value"],
                                 mode="markers",
                                 name="long",
                                 marker={"size": 3, "opacity": 0.5}))
        fig.add_trace(go.Scatter(x=self.data[self.data["position"] == "short"].index,
                                 y=self.data[self.data["position"] == "short"]["value"],
                                 mode="markers",
                                 name="short",
                                 marker={"size": 3, "opacity": 0.5}))
        self._vis_trading_signal(fig)

        if html:
            now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            fig.write_html(f"{now}.html")
        else:
            fig.show()


class Backtest():
    def _init_backtest(self):
        self.trading_log = {"position": [], "entry_date": [], "entry_value": [],
                            "exit_date": [], "exit_value": []}

    def _set_cost(self, tax=0.002, sell_fee=0.00015, buy_fee=0.00015, slippage=0):
        self.sell_cost = tax+sell_fee+slippage
        self.buy_cost = buy_fee+slippage

    def _register_entry(self, position, date, value):
        self.trading_log["position"].append(position)
        self.trading_log["entry_date"].append(date)
        self.trading_log["entry_value"].append(value)

    def _register_exit(self, date, value):
        self.trading_log["exit_date"].append(date)
        self.trading_log["exit_value"].append(value)

    def _add_return_column(self):
        tl = self.trading_log
        sell_c = self.sell_cost
        buy_c = self.buy_cost
        tl.loc[tl["position"] == "long", "rtrn"] = \
            round((tl["exit_value"]*(1-sell_c)-tl["entry_value"]*(1+buy_c)) / tl["entry_value"],4)
        tl.loc[tl["position"] == "short", "rtrn"] = \
            round((tl["entry_value"]*(1-sell_c)-tl["exit_value"]*(1+buy_c)) / tl["exit_value"],4)

    def _signal_side(self, sig_side="long"):
        if sig_side == "all":
            pass
        else:
            self.trading_log = self.trading_log.loc[self.trading_log["position"] == sig_side]
            self.trading_log.index = range(len(self.trading_log))

    def backtest(self, signal_side="long"):
        self._init_backtest()
        buy_entry_state = False
        sell_entry_state = False
        for i in range(len(self.data)):
            date = self.data.index[i]
            value = self.data.iloc[i]["value"]
            position = self.data.iloc[i]["position"]
            entry_buy_cond = ((position == "long") & (self.data.iloc[i]["entry_buy"]))
            entry_sell_cond = ((position == "short") & (self.data.iloc[i]["entry_sell"]))
            exit_buy_cond = (((position == "nothing") | (position == "short")) & (self.data.iloc[i]["exit_buy"]))
            exit_sell_cond = (((position == "nothing") | (position == "long")) & (self.data.iloc[i]["exit_sell"]))

            if entry_buy_cond:
                self._register_entry(position, date, value)
                buy_entry_state = True
            if entry_sell_cond:
                self._register_entry(position, date, value)
                sell_entry_state = True
            if exit_buy_cond:
                if buy_entry_state:
                    self._register_exit(date, value)
                    buy_entry_state = False
                else:
                    pass
            if exit_sell_cond:
                if sell_entry_state:
                    self._register_exit(date, value)
                    sell_entry_state = False
                else:
                    pass

        if self.data.iloc[-1]["position"] != "nothing":
            self._register_exit(self.data.index[-1], self.data.iloc[-1]["value"])

        self.trading_log = pd.DataFrame(self.trading_log)
        self._add_return_column()
        self._signal_side(signal_side)
        self.trading_log["acc_rtrn"] = self.trading_log["rtrn"].cumsum()


class Visualization():
    def _get_bar_width_tradeoff(self):
        '''
        bar chart에서 투자 기간에 따른 bar width와 trade off 를 반환
        '''
        bar_width = self.trading_log["exit_date"] - self.trading_log["entry_date"]
        bar_width = bar_width.astype("int64") / 1000000  # microseconds 단위로 변환
        bar_tradeoff = bar_width.astype("int64") / 2000000  # 1/2 microseconds 만큼 이동

        return bar_width, bar_tradeoff

    def _set_color(self, df, column, value_color: dict):
        '''
        color 변환용 값 반환
        value_color : ex){"buy": "orange", "sell": "purple"}
        '''
        df_col = df.copy()
        for value, color in value_color.items():
            df_col.loc[df_col[column] == value, "color"] = color
        df_col = df_col["color"]

        return df_col

    def _add_trading_signal(self, fig):
        for i in range(len(self.trading_log)):
            position = self.trading_log.iloc[i]["position"]
            entry_date = self.trading_log.iloc[i]["entry_date"]
            entry_value = self.trading_log.iloc[i]["entry_value"]
            exit_date = self.trading_log.iloc[i]["exit_date"]
            exit_value = self.trading_log.iloc[i]["exit_value"]
            if position == "long":
                fig.add_annotation(x=entry_date,
                                   y=entry_value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="red",
                                   ax=0,
                                   ay=25,
                                   arrowwidth=1.5)
                fig.add_annotation(x=exit_date,
                                   y=exit_value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="orange",
                                   ax=0,
                                   ay=-25,
                                   arrowwidth=1.5)
            if position == "short":
                fig.add_annotation(x=entry_date,
                                   y=entry_value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="blue",
                                   ax=0,
                                   ay=-25,
                                   arrowwidth=1.5)
                fig.add_annotation(x=exit_date,
                                   y=exit_value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="purple",
                                   ax=0,
                                   ay=25,
                                   arrowwidth=1.5)

    def visualize_1(self, html=True):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        bar_width, bar_tradeoff = self._get_bar_width_tradeoff()
        fig.add_trace(go.Scatter(x=self.data.index,
                                 y=self.data["value"],
                                 mode="markers",
                                 marker={"size": 3,
                                         "opacity": 0.5},
                                 name="value"), secondary_y=False)
        fig.add_trace(go.Scatter(x=self.trading_log["entry_date"],
                                 y=self.trading_log["entry_value"],
                                 mode="markers",
                                 marker={"size": 4},
                                 name="entry"
                                 ), secondary_y=False)
        fig.add_trace(go.Scatter(x=self.trading_log["exit_date"],
                                 y=self.trading_log["exit_value"],
                                 mode="markers",
                                 marker={"size": 4},
                                 name="exit"
                                 ), secondary_y=False)
        fig.add_trace(go.Scatter(x=self.trading_log["exit_date"],
                                 y=self.trading_log["acc_rtrn"],
                                 mode="lines",
                                 name="acc_rtrn"), secondary_y=True)
        fig.add_trace(go.Bar(x=self.trading_log["entry_date"],
                             y=self.trading_log["rtrn"],
                             name="rtrn",
                             opacity=0.4,
                             width=bar_width,
                             offset=bar_tradeoff,
                             text=self.trading_log["rtrn"],
                             textposition="outside",
                             textangle=0), secondary_y=True)
        self._add_trading_signal(fig)

        if html:
            now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            fig.write_html(f"{now}.html")
        else:
            fig.show()


class Strategy(Algorithm, Backtest, Visualization):
    def __init__(self, df, column):
        self.raw_data = df[[column]].copy()
        self.data = df[[column]].copy()
        self.column = column
        self._set_cost(tax=0.002, sell_fee=0.00015, buy_fee=0.00015, slippage=0)

