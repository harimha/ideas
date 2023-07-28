import pandas as pd
import plotly.graph_objects as go

from abc import ABC, abstractmethod
from datetime import datetime
from pandas.api.types import is_list_like


class Algorithm(ABC):

    @abstractmethod
    def _set_sub_indicators(self):
        pass

    @abstractmethod
    def _entry_buy_condition(self, df_indi):
        pass

    @abstractmethod
    def _entry_sell_condition(self, df_indi):
        pass

    @abstractmethod
    def _exit_buy_condition(self, df_indi):
        pass

    @abstractmethod
    def _exit_sell_condition(self, df_indi):
        pass

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

    def execute_algorithm(self):
        df_indi = self._set_sub_indicators()
        df_cond = self._set_condition(df_indi)
        df_position = self._set_position(df_cond)
        df_algo = self._set_signals(df_position)

        return df_algo


class Backtest():
    def __init__(self):
        self.set_cost()

    def _register_entry(self, trading_log, position, date, value):
        trading_log["position"].append(position)
        trading_log["entry_date"].append(date)
        trading_log["entry_value"].append(value)

    def _register_exit(self, trading_log, date, value):
        trading_log["exit_date"].append(date)
        trading_log["exit_value"].append(value)

    def _add_rtrn(self, df_backtest):
        long_rtrn = (df_backtest["exit_value"]*(1-self.sell_cost)-df_backtest["entry_value"]*(1+self.buy_cost))/df_backtest["entry_value"]
        short_rtrn = (df_backtest["entry_value"]*(1-self.sell_cost)-df_backtest["exit_value"]*(1+self.buy_cost))/df_backtest["exit_value"]
        df_backtest.loc[df_backtest["position"]=="long", "rtrn"] = long_rtrn
        df_backtest.loc[df_backtest["position"]=="short", "rtrn"] = short_rtrn

        return df_backtest

    def _add_acc_rtrn(self, df_backtest):
        df_backtest["acc_rtrn"] = df_backtest["rtrn"].cumsum()

        return df_backtest

    def set_cost(self, tax=0.002, sell_fee=0.00015, buy_fee=0.00015, slippage=0):
        self.sell_cost = tax+sell_fee+slippage
        self.buy_cost = buy_fee+slippage

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
        df_backtest = self._add_rtrn(df_backtest)
        df_backtest = self._add_acc_rtrn(df_backtest)

        return df_backtest


class Visualize():

    def init_fig(self):
        fig = go.Figure()
        return fig

    def fig_show(self, fig, name=None, html=True):
        if html:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            fig.write_html(f"html/{name}_{now}.html")
        else:
            fig.show()

    def _get_bar_width_tradeoff(self, df_backtest):
        '''
        bar chart에서 투자 기간에 따른 bar width와 trade off 를 반환
        '''
        bar_width = df_backtest["exit_date"] - df_backtest["entry_date"]
        bar_width = bar_width.astype("int64") / 1000000  # microseconds 단위로 변환
        bar_tradeoff = bar_width.astype("int64") / 2000000  # 1/2 microseconds 만큼 이동

        return bar_width, bar_tradeoff

    def _get_color_df(self, df, column, value_color: dict):
        '''
        color 변환용 값 반환
        value_color : ex){"buy": "orange", "sell": "purple"}
        '''
        df_col = df.copy()
        for value, color in value_color.items():
            df_col.loc[df_col[column] == value, "color"] = color
        df_col = df_col["color"]

        return df_col

    def _add_signal(self, fig, df_value, side="long"):
        if side == "long":
            for i in range(len(df_value)):
                date = df_value.index[i]
                value = df_value.iloc[i]
                fig.add_annotation(x=date,
                                   y=value,
                                   showarrow=True,
                                   arrowhead=2,
                                   yshift=-10,
                                   ax=0,
                                   ay=25,
                                   arrowwidth=1.5)
        else:
            for i in range(len(df_value)):
                date = df_value.index[i]
                value = df_value.iloc[i]
                fig.add_annotation(x=date,
                                   y=value,
                                   showarrow=True,
                                   arrowhead=2,
                                   ax=0,
                                   ay=-25,
                                   arrowwidth=1.5)

        return fig

    def _add_trading_signal(self, df_backtest, fig):
        for i in range(len(df_backtest)):
            position = df_backtest.iloc[i]["position"]
            entry_date = df_backtest.iloc[i]["entry_date"]
            entry_value = df_backtest.iloc[i]["entry_value"]
            exit_date = df_backtest.iloc[i]["exit_date"]
            exit_value = df_backtest.iloc[i]["exit_value"]
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

        return fig

    def _add_entry_exit_signal(self, df_algo, fig):
        pass

    def vis_indicator(self, fig, df_indi, mode):
        columns = df_indi.columns
        if is_list_like(columns):
            for col in columns:
                fig.add_trace(go.Scatter(x=df_indi.index,
                                         y=df_indi[col],
                                         mode=mode,
                                         name=col))
        else:
            fig.add_trace(go.Scatter(x=df_indi.index,
                                     y=df_indi[columns],
                                     mode=mode,
                                     name=columns))

        return fig

    def vis_entry_exit(self, fig, df_algo):
        df_nbc = df_algo.loc[df_algo["entry_buy_cond"], "value"]
        df_nsc = df_algo.loc[df_algo["entry_sell_cond"], "value"]
        # df_xbc = df_algo.loc[df_algo["exit_buy_cond"], "value"]
        # df_xsc = df_algo.loc[df_algo["exit_sell_cond"], "value"]

        fig = self._add_signal(fig, df_nbc, "long")
        fig = self._add_signal(fig, df_nsc, "short")
        # fig = self._add_signal(fig, df_xbc, "short")
        # fig = self._add_signal(fig, df_xsc, "long")

        return fig

    def vis_algo(self,
                 entry_buy_cond=True,
                 entry_sell_cond=True,
                 exit_buy_cond=True,
                 exit_sell_cond=True,
                 mode="markers",
                 name="test", html=True):
        conditions = {"entry_buy_cond":entry_buy_cond,
                "entry_sell_cond": entry_sell_cond,
                "exit_buy_cond": exit_buy_cond,
                "exit_sell_cond": exit_sell_cond}
        df_algo = self.execute_algorithm()
        fig = go.Figure()
        fig = self.vis_indicator(fig, mode="lines")

        for condition_name, condition in conditions.items():
            cond_df = df_algo.loc[df_algo[condition_name], "value"]
            fig.add_trace(go.Scatter(x=cond_df.index,
                                     y=cond_df,
                                     mode=mode,
                                     name=condition_name))

        # True에 해당하는 것만 저장
        # 최대 겹치는 6가지 경우의 수
        nbc_nsc = df_algo["entry_buy_cond"]&df_algo["entry_sell_cond"]
        nbc_xbc = df_algo["entry_buy_cond"]&df_algo["exit_buy_cond"]
        nbc_xsc = df_algo["entry_buy_cond"]&df_algo["exit_sell_cond"]
        nsc_xbc = df_algo["entry_sell_cond"]&df_algo["exit_buy_cond"]
        nsc_xsc = df_algo["entry_sell_cond"]&df_algo["exit_sell_cond"]
        xbc_xsc = df_algo["exit_buy_cond"]&df_algo["exit_sell_cond"]
        conditions = {"nbc_nsc": nbc_nsc,
                      "nbc_xbc": nbc_xbc,
                      "nbc_xsc": nbc_xsc,
                      "nsc_xbc": nsc_xbc,
                      "nsc_xsc": nsc_xsc,
                      "xbc_xsc": xbc_xsc,
                      }
        for condition_name, condition in conditions.items():
            cond_df = df_algo.loc[condition, "value"]
            fig.add_trace(go.Scatter(x=cond_df.index,
                                     y=cond_df,
                                     mode=mode,
                                     name=condition_name))


        self.fig_show(fig, name, html)


    def vis_backtest(self):
        pass

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

