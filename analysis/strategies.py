import pandas as pd
import numpy as np
import fdata.api as api
import plotly.graph_objects as go
from analysis.indicator import sma
from pandas.api.types import is_list_like
from datetime import datetime
from plotly.subplots import make_subplots


class Singleton():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class Strategy(Singleton):
    def __init__(self, df, column):
        self.raw_data = df.copy()
        self.column = column
        self._set_cost()

    def _init_execute(self):
        self.data = self.raw_data.copy()

    def _init_backtest(self):
        self.data_lst = []
        self.base_value = None
        self.result = {"date": [], "signal": [], "value": [], "rtrn": [], "max_rtrn": [],
                       "min_rtrn": [], "avg_rtrn": []}

    def _set_cost(self, tax=0.002, oneside_fee=0.00015, slippage=0):
        self.sell_cost = tax+oneside_fee+slippage
        self.buy_cost = oneside_fee+slippage

    def _set_mode(self, i, mode="buy"):
        self.data_lst = []
        self.base_value = self.data.iloc[i][self.column]
        self.result["date"].append(self.data.index[i])
        self.result["value"].append(self.base_value)
        self.result["signal"].append(mode)

    def _write_value(self, i, mode="buy"):
        if mode == "buy":
            max_rtrn = (max(self.data_lst)*(1-self.sell_cost)-self.base_value*(1-self.buy_cost)) / self.base_value
            min_rtrn = (min(self.data_lst)*(1-self.sell_cost)-self.base_value*(1-self.buy_cost)) / self.base_value
            avg_rtrn = (np.mean(self.data_lst)*(1-self.sell_cost)-self.base_value*(1-self.buy_cost)) / self.base_value
            re =  (self.data.iloc[i][self.column]*(1-self.sell_cost)-self.base_value*(1-self.buy_cost)) / self.base_value
        elif mode == "sell":
            max_rtrn = (self.base_value*(1-self.sell_cost)-min(self.data_lst)*(1-self.buy_cost)) / min(self.data_lst)
            min_rtrn = (self.base_value*(1-self.sell_cost)-max(self.data_lst)*(1-self.buy_cost)) / max(self.data_lst)
            avg_rtrn = (self.base_value*(1-self.sell_cost)-np.mean(self.data_lst)*(1-self.buy_cost)) / np.mean(self.data_lst)
            re = (self.base_value*(1-self.sell_cost)-self.data.iloc[i][self.column]*(1-self.buy_cost)) / self.data.iloc[i][self.column]
        else:
            raise ValueError("올바르지 않은 mode 값 입니다 (only 'buy' or 'sell')")
        self.result["max_rtrn"].append(max_rtrn)
        self.result["min_rtrn"].append(min_rtrn)
        self.result["avg_rtrn"].append(avg_rtrn)
        self.result["rtrn"].append(re)

    def _cut_laststate(self):
        self.result["date"].pop()
        self.result["value"].pop()
        self.result["signal"].pop()

    def _calculate_laststate(self):
        if self.data.iloc[-1][f"{self.column}_state"] == "bull":
            self._write_value(-1, mode="buy")
        else:
            self._write_value(-1, mode="sell")

    def _add_state_signal(self):
        state_now = self.data[f"{self.column}_state"]
        state_before = self.data[f"{self.column}_state"].shift(1)
        buy_sig = ((state_now == "bull") & (state_before == "bear"))
        sell_sig = ((state_now == "bear") & (state_before == "bull"))
        self.data.loc[buy_sig, f"{self.column}_signal"] = "buy"
        self.data.loc[sell_sig, f"{self.column}_signal"] = "sell"
        self.data = self.data.fillna("hold")

    def _algorithm(self, *args, **kwargs):
        pass

    def execute(self, *args, **kwargs):
        self._init_execute()
        self._algorithm(*args, **kwargs)
        self._add_state_signal()

    def backtest(self, sig_side="buy"):
        self._init_backtest()
        counts = len(self.data)
        investment_begin = False
        for i in range(counts):
            data = self.data.iloc[i][self.column]
            sig = self.data.iloc[i][f"{self.column}_signal"]
            self.data_lst.append(self.data.iloc[i][self.column])
            if sig == "buy":
                if investment_begin:
                    self._write_value(i, mode="sell")
                    self._set_mode(i, mode="buy")
                else:
                    investment_begin = True
                    self._set_mode(i, mode="buy")
            elif sig == "sell":
                if investment_begin:
                    self._write_value(i, mode="buy")
                    self._set_mode(i, mode="sell")
                else:
                    investment_begin = True
                    self._set_mode(i, mode="sell")


        # self._cut_laststate()
        self._calculate_laststate()
        df_result = pd.DataFrame(self.result)
        if sig_side == "all":
            pass
        else:
            df_result = df_result.loc[df_result["signal"] == sig_side]
        df_result.index = range(len(df_result))

        return df_result



class Visualization():
    def _get_bar_width_tradeoff(self, df_data, df_result):
        '''
        bar chart에서 투자 기간에 따른 bar width와 trade off 를 반환
        '''
        bar_width = df_result["date"].shift(-1) - df_result["date"]
        bar_width = bar_width.fillna(df_data.index[-1] - df_result["date"].iloc[-1])
        bar_width = bar_width.astype("int64") / 1000000  # microseconds 단위로 변환
        bar_tradeoff = bar_width.astype("int64") / 2000000 # 1/2 microseconds 만큼 이동

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

    def _add_trading_signal(self, df_result, fig):
        for i in range(len(df_result)):
            date = df_result.iloc[i]["date"]
            value = df_result.iloc[i]["value"]
            sig = df_result.iloc[i]["signal"]
            if sig == "buy":
                fig.add_annotation(x=date,
                                   y=value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="red",
                                   ax=0,
                                   ay=25,
                                   arrowwidth=1.5,
                                   secondary_y=False
                                   )
            elif sig == "sell":
                fig.add_annotation(x=date,
                                   y=value,
                                   showarrow=True,
                                   arrowhead=2,
                                   arrowcolor="blue",
                                   ax=0,
                                   ay=-25,
                                   arrowwidth=1.5,
                                   secondary_y=False)

    def visualize_1(self, df_data, df_result, html=True):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        bar_width, bar_tradeoff = self._get_bar_width_tradeoff(df_data, df_result)
        color_data = self._set_color(df_data, df_data.columns[-2], {"bull":"lightcoral", "bear":"lightskyblue"})
        color_trading = self._set_color(df_result, "signal", {"buy":"red", "sell":"blue"})
        color_return = self._set_color(df_result, "signal", {"buy":"orange", "sell":"purple"})
        fig.add_trace(go.Scatter(x=df_data.index,
                                 y=df_data["종가"],
                                 mode="markers",
                                 marker={"size": 3,
                                         "opacity": 0.5,
                                         "color": color_data},
                                 name="종가"),secondary_y=False)
        fig.add_trace(go.Scatter(x=df_result["date"],
                                 y=df_result["value"],
                                 mode="markers",
                                 marker={"size": 4,
                                         "color": color_trading},
                                 name="signal"
                                 ),secondary_y=False)
        fig.add_trace(go.Scatter(x=df_result["date"],
                                 y=df_result["acc_rtrn"],
                                 mode="lines",
                                 name="acc_rtrn"), secondary_y=True)
        fig.add_trace(go.Bar(x=df_result["date"],
                             y=df_result["rtrn"],
                             marker={"color": color_return},
                             name="rtrn",
                             opacity=0.4,
                             width=bar_width,
                             offset=bar_tradeoff,
                             text=df_result["rtrn"],
                             textposition="outside",
                             textangle=0),secondary_y=True)
        self._add_trading_signal(df_result, fig)

        if html :
            now = datetime.now().strftime("%Y%m%d%H%M%S")
            fig.write_html(f"{now}.html")
        else:
            fig.show()


class GoldenDeadCross(Strategy, Visualization):
    def __init__(self, df, column, short, long):
        super().__init__(df, column)
        self.execute(short, long)

    def _algorithm(self, short, long):
        self.data = sma(self.data, self.column, [short, long])
        self.data = self.data.dropna()
        golden = self.data[f"{self.column}_sma{short}"] >= self.data[f"{self.column}_sma{long}"]
        self.data.loc[golden, f"{self.column}_state"] = "bull"
        self.data = self.data.fillna("bear")

    def backtest(self, sig_side="buy"):
        df = super().backtest(sig_side)
        df = df[["date", "signal", "value", "rtrn"]]
        df["acc_rtrn"] = round(df["rtrn"].cumsum(),4)
        df["rtrn"] = round(df["rtrn"],4)

        return df

    def visualize_1(self, html=True):
        df_result = self.backtest()
        super().visualize_1(self.data, df_result, html)





df= api.stock_ohlcv("에이스침대", "20050101", "20231201")
GDC = GoldenDeadCross(df, "종가", 20, 60)
GDC.visualize_1()

