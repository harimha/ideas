import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pandas.api.types import is_list_like
from analysis.visualization import Plot
import numpy as np


class Algorithm(ABC):

    @abstractmethod
    def set_sub_indicators(self):
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

    def get_condition_df(self, df_indi):
        df_cond = df_indi.copy()
        df_cond["entry_buy_cond"] = self._entry_buy_condition(df_indi)
        df_cond["entry_sell_cond"] = self._entry_sell_condition(df_indi)
        df_cond["exit_buy_cond"] = self._exit_buy_condition(df_indi)
        df_cond["exit_sell_cond"] = self._exit_sell_condition(df_indi)

        return df_cond

    def get_position_df(self, df_cond):
        df_position = df_cond.iloc[:,:df_cond.columns.get_loc("entry_buy_cond")].copy()
        positions = []
        pos = "nothing"
        for i in range(len(df_cond)):
            if pos == "nothing":
                if df_cond.iloc[i]["entry_buy_cond"]:
                    pos = "long"
                elif df_cond.iloc[i]["entry_sell_cond"]:
                    pos = "short"
            elif pos == "long":
                if df_cond.iloc[i]["exit_buy_cond"]:
                    pos = "nothing"
                if df_cond.iloc[i]["entry_sell_cond"]:
                    pos = "short"
            elif pos == "short":
                if df_cond.iloc[i]["exit_sell_cond"]:
                    pos = "nothing"
                if df_cond.iloc[i]["entry_buy_cond"]:
                    pos = "long"
            positions.append(pos)

        df_position["position"] = positions

        return df_position

    def get_trading_signal_df(self, df_position):
        df_signal = df_position.copy()
        pos_now = df_signal["position"]
        pos_bef = df_signal["position"].shift(1)
        df_signal["entry_buy"] = ((pos_now == "long") & ((pos_bef == "nothing") | (pos_bef == "short")))
        df_signal["entry_sell"] = ((pos_now == "short") & ((pos_bef == "nothing") | (pos_bef == "long")))
        df_signal["exit_buy"] = (((pos_now == "nothing") | (pos_now == "short")) & ((pos_bef == "long")))
        df_signal["exit_sell"] = (((pos_now == "nothing") | (pos_now == "long")) & ((pos_bef == "short")))

        return df_signal

    def execute_algorithm(self):
        df_algo = self.get_trading_signal_df(self.get_position_df(self.get_condition_df(self.set_sub_indicators())))

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
        df_backtest.loc[df_backtest["position"]=="long", "rtrn"] = round(long_rtrn,4)
        df_backtest.loc[df_backtest["position"]=="short", "rtrn"] = round(short_rtrn,4)

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

    def _set_arrow_annotation(self, x, y, color, side="long"):
        if side == "long":
            annotation = dict(x=x, y=y, showarrow=True, arrowhead=2, arrowcolor=color, ax=0, ay=35, arrowwidth=2.5, yshift=-3)
        elif side == "short":
            annotation = dict(x=x, y=y, showarrow=True, arrowhead=2, arrowcolor=color, ax=0, ay=-35, arrowwidth=2.5, yshift=3)
        else:
            raise ValueError("Only 'short' or 'long' is valid")

        return annotation

    def _add_backtest_trading_arrow(self, fig, df_backtest):
        annotations = []
        for i in range(len(df_backtest)):
            if df_backtest.iloc[i]["position"]=="long":
                annotations.append(self._set_arrow_annotation(
                    x=df_backtest.iloc[i]["entry_date"],
                    y=df_backtest.iloc[i]["entry_value"],
                    color="red",
                    side="long"))
                annotations.append(self._set_arrow_annotation(
                    x=df_backtest.iloc[i]["exit_date"],
                    y=df_backtest.iloc[i]["exit_value"],
                    color="orange",
                    side="short"))
            elif df_backtest.iloc[i]["position"]=="short":
                annotations.append(self._set_arrow_annotation(
                    x=df_backtest.iloc[i]["entry_date"],
                    y=df_backtest.iloc[i]["entry_value"],
                    color="blue",
                    side="short"))
                annotations.append(self._set_arrow_annotation(
                    x=df_backtest.iloc[i]["exit_date"],
                    y=df_backtest.iloc[i]["exit_value"],
                    color="purple",
                    side="long"))
        fig.update_layout(annotations=annotations)

    def _add_algo_signal_arrow(self, fig, df_algo, nb=True, ns=True, xb=True, xs=True):
        sig = {"exit_buy":{"visible":xb, "color":"orange", "side":"short"},
               "exit_sell":{"visible":xs, "color":"purple", "side":"long"},
               "entry_buy":{"visible":nb, "color":"red", "side":"long"},
               "entry_sell":{"visible":ns, "color":"blue", "side":"short"}}

        annotations = []
        for sig_type, sig_val in sig.items():
            if sig_val["visible"]:
                df = df_algo.loc[df_algo[sig_type], "value"]
                for i in range(len(df)):
                    annotations.append(self._set_arrow_annotation(x=df.index[i],
                                                                  y=df.iloc[i],
                                                                  color=sig_val["color"],
                                                                  side=sig_val["side"]))
        fig.update_layout(annotations=annotations)

        return fig

    def _xaxis_datetime_range_break(self, fig, dt_series):
        dt_all = pd.date_range(start=dt_series[0], end=dt_series[-1])
        dt_breaks = [day for day in dt_all if not day in dt_series]
        fig.update_xaxes(
            rangebreaks=[dict(values=dt_breaks)]
        )

        return fig

    def _set_background_color_dtrange(self, start_dt, end_dt, color, y0=0, y1=1):
        shape = dict(
            type="rect",
            xref="x",
            yref="paper",
            x0=start_dt - timedelta(hours=12),
            x1=end_dt + timedelta(hours=12),
            y0=y0,
            y1=y1,
            line={"width": 0},
            fillcolor=color,
            opacity=0.3,
            layer="below")

        return shape

    def _set_background_color_df(self, df, color, y0=0, y1=1):
        shapes = []
        for day in df.index:
            shapes.append(self._set_background_color_dtrange(day, day, color, y0=y0, y1=y1))

        return shapes

    def _update_layout_shape(self, fig, *shapes):
        s = []
        for shape in shapes:
            s += shape
        fig.update_layout(shapes=s)

        return fig

    def _get_bar_width_offset(self, df_backtest):
        '''
        bar chart에서 투자 기간에 따른 bar width와 trade off 를 반환
        '''
        bar_width = df_backtest["exit_date"] - df_backtest["entry_date"]
        bar_width = bar_width.astype("int64") / 1000000  # microseconds 단위로 변환
        bar_offset = bar_width.astype("int64") / 2000000  # 1/2 microseconds 만큼 이동

        return bar_width, bar_offset

    #### 수정중
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

    # visualize
    def vis_value(self, fig, df_value, rows=1, cols=1, y2=False):
        fig = Plot().line_plot(fig,
                               x=df_value.index,
                               y=df_value,
                               line={"color": "DimGray"},
                               marker={"opacity": 0.5},
                               name="value",
                               mark=True, rows=rows, cols=cols, y2=y2)
        fig = self._xaxis_datetime_range_break(fig, df_value.index)

        return fig

    def vis_sub_indicator(self, fig, df_indi, rows=1, cols=1, y2=False):
        columns = df_indi.columns[1:]
        if is_list_like(columns):
            for column in columns:
                fig = Plot().line_plot(fig,
                                x=df_indi.index,
                                y=df_indi[column],
                                marker={"opacity": 0.5},
                                name=column,
                                mark=True,
                                rows=rows, cols=cols, y2=y2)
        else:
            fig = Plot().line_plot(fig,
                            x=df_indi.index,
                            y=df_indi[columns],
                            marker={"opacity": 0.5},
                            name=columns,
                            mark=True,
                            rows=rows, cols=cols, y2=y2)
        fig = self._xaxis_datetime_range_break(fig, df_indi.index)

        return fig

    def vis_value_indicator(self, fig, df_indi, rows=1, cols=1, y2=False):
        fig = self.vis_sub_indicator(fig, df_indi, rows, cols, y2)
        fig = self.vis_value(fig, df_indi["value"], rows, cols, y2)
        fig = self._xaxis_datetime_range_break(fig, df_indi.index)

        return fig

    def vis_entry_exit_condition(self, fig, df_cond, nbc=True, nsc=True, xbc=True, xsc=True,
                                 vis_indi=True, rows=1, cols=1, y0=0, y1=1, y2=False):
        if vis_indi:
            df_indi = df_cond.iloc[:, :df_cond.columns.get_loc("entry_buy_cond")].copy()
            fig = self.vis_value_indicator(fig, df_indi, rows=rows, cols=cols, y2=y2)
        else:
            fig = self.vis_value(fig, df_cond["value"], rows=rows, cols=cols, y2=y2)
        cond = {"entry_buy_cond":{"visible":nbc,"color":"lightcoral"},
                "entry_sell_cond":{"visible":nsc,"color":"LightSteelBlue"},
                "exit_buy_cond":{"visible":xbc,"color":"lightskyblue"},
                "exit_sell_cond":{"visible":xsc,"color":"LightSalmon"}}
        shapes=[]
        for cond_name, cond_val in cond.items():
            if cond_val["visible"]:
                df = df_cond.loc[df_cond[cond_name],"value"]
                shape = self._set_background_color_df(df, cond_val["color"],y0=y0, y1=y1)
                shapes += shape
        fig = self._update_layout_shape(fig, shapes)
        fig = self._xaxis_datetime_range_break(fig, df_cond.index)

        return fig

    def vis_position(self, fig, df_position, vis_indi=True, rows=1, cols=1, y0=0, y1=1, y2=False):
        if vis_indi:
            df_indi = df_position.iloc[:, :df_position.columns.get_loc("position")].copy()
            fig = self.vis_value_indicator(fig, df_indi, rows=rows, cols=cols, y2=y2)
        else:
            fig = self.vis_value(fig, df_position["value"], rows=rows, cols=cols, y2=y2)

        position = {"long":"LightSalmon",
                    "short":"LightSteelBlue"}
        shapes = []
        for position_type, color in position.items():
            df = df_position.loc[df_position["position"]==position_type, "value"]
            shape = self._set_background_color_df(df, color, y0=y0, y1=y1)
            shapes += shape
        fig = self._update_layout_shape(fig, shapes)
        fig = self._xaxis_datetime_range_break(fig, df_position.index)

        return fig

    def vis_trading_signal(self, fig, df_algo, vis_indi=True, nb=True, ns=True, xb=True, xs=True,
                 rows=1, cols=1, y0=0, y1=1, y2=False):
        if vis_indi:
            df_indi = df_algo.iloc[:, :df_algo.columns.get_loc("position")].copy()
            fig = self.vis_value_indicator(fig, df_indi, rows, cols, y2)
        else:
            fig = self.vis_value(fig, df_algo["value"], rows, cols, y2)
        fig = self._add_algo_signal_arrow(fig, df_algo, nb, ns, xb, xs)
        fig = self._xaxis_datetime_range_break(fig, df_algo.index)

        return fig

    def vis_algo(self, fig, df_algo, vis_indi=True, nb=True, ns=True, xb=True, xs=True,
                 rows=1, cols=1, y0=0, y1=1, y2=False):
        df_position = df_algo.iloc[:, :df_algo.columns.get_loc("entry_buy")].copy()
        fig = self.vis_position(fig, df_position, vis_indi, rows, cols, y0, y1, y2=False)
        fig = self._add_algo_signal_arrow(fig, df_algo, nb, ns, xb, xs)
        fig = self._xaxis_datetime_range_break(fig, df_algo.index)

        return fig

    def vis_rtrn(self, fig, df_backtest, rows=1, cols=1, y2=False):
        bar_width, bar_offset = self._get_bar_width_offset(df_backtest)
        fig = Plot().line_plot(fig,
                               x=df_backtest["exit_date"],
                               y=df_backtest["acc_rtrn"],
                               name="acc_rtrn",
                               mark=True,
                               rows=rows,
                               cols=cols,
                               y2=y2)
        fig = Plot().bar_chart(fig,
                               x=df_backtest["entry_date"],
                               y=df_backtest["rtrn"],
                               text=df_backtest["rtrn"],
                               width=bar_width,
                               offset=bar_offset,
                               name="rtrn",
                               rows=rows,
                               cols=cols,
                               y2=y2)
        return fig

    def vis_backtest(self, fig, df_algo, df_backtest, vis_indi=True):
        fig = self.vis_trading_signal(fig, df_algo, rows=1, cols=1)
        self._add_backtest_trading_arrow(fig, df_backtest)
        fig = self.vis_rtrn(fig, df_backtest, rows=1, cols=1, y2=True)
        fig = self._xaxis_datetime_range_break(fig, df_algo.index)

        return fig

