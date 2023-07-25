import pandas as pd
import numpy as np
import fdata.api as api
import plotly.graph_objects as go
from analysis.indicator import sma
from pandas.api.types import is_list_like


class Strategy():
    def __init__(self, df, column):
        self.data = df.copy()
        self.column = column
        self.tax_fee = 0
        self.slippage = 0
        self.data_lst = []
        self.base_value = None
        self.flag = None
        self.sell = {"date": [], "value": [], "rtrn": [], "max_rtrn": [], "min_rtrn": [], "avg_rtrn": []}
        self.buy = {"date": [], "value": [], "rtrn": [], "max_rtrn": [], "min_rtrn": [], "avg_rtrn": []}
        self.df_buy = None
        self.df_sell = None

    def _init_mode(self, i, mode="buy"):
        if mode == "buy":
            self.data_lst = []
            self.flag = self.data.iloc[i][f"{self.column}_signal"]
            self.base_value = self.data.iloc[i][self.column]
            self.buy["date"].append(self.data.index[i])
            self.buy["value"].append(self.base_value)

        elif mode == "sell":
            self.data_lst = []
            self.flag = self.data.iloc[i][f"{self.column}_signal"]
            self.base_value = self.data.iloc[i][self.column]
            self.sell["date"].append(self.data.index[i])
            self.sell["value"].append(self.base_value)
        else:
            raise ValueError("올바르지 않은 mode 값 입니다 (only 'buy' or 'sell')")

    def _write_value(self, i, mode="buy"):
        if mode == "buy":
            max_rtrn = max(self.data_lst) / self.base_value - 1
            min_rtrn = min(self.data_lst) / self.base_value - 1
            avg_rtrn = np.mean(self.data_lst) / self.base_value  - 1
            re =  self.data.iloc[i][self.column] / self.base_value - 1
            self.buy["max_rtrn"].append(max_rtrn)
            self.buy["min_rtrn"].append(min_rtrn)
            self.buy["avg_rtrn"].append(avg_rtrn)
            self.buy["rtrn"].append(re)
        elif mode == "sell":
            max_rtrn = self.base_value / min(self.data_lst) - 1
            min_rtrn = self.base_value / max(self.data_lst) - 1
            avg_rtrn = self.base_value / np.mean(self.data_lst) - 1
            re = self.base_value / self.data.iloc[i][self.column] - 1
            self.sell["max_rtrn"].append(max_rtrn)
            self.sell["min_rtrn"].append(min_rtrn)
            self.sell["avg_rtrn"].append(avg_rtrn)
            self.sell["rtrn"].append(re)
        else:
            raise ValueError("올바르지 않은 mode 값 입니다 (only 'buy' or 'sell')")

    def _cut_laststate(self):
        last_state = self.data[f"{self.column}_state"][-1:].iloc[0]
        if last_state == 1:
            self.buy["date"].pop()
            self.buy["value"].pop()
        else:
            self.sell["date"].pop()
            self.sell["value"].pop()

    def _add_state_signal(self):
        buy_sig = ((self.data[f"{self.column}_state"] == 1) & (self.data[f"{self.column}_state"].shift(1) == 0))
        sell_sig = ((self.data[f"{self.column}_state"] == 0) & (self.data[f"{self.column}_state"].shift(1) == 1))
        self.data.loc[buy_sig, f"{self.column}_signal"] = "buy"
        self.data.loc[sell_sig, f"{self.column}_signal"] = "sell"
        self.data = self.data.fillna("hold")

    def execute(self):
        self._add_state_signal()

    def backtest(self):
        counts = len(self.data)
        for i in range(counts):
            self.data_lst.append(self.data.iloc[i][self.column])
            if self.data.iloc[i][f"{self.column}_signal"] == "buy":
                if self.flag is None:
                    self._init_mode(i, mode="buy")
                else:
                    self._write_value(i, mode="sell")
                    self._init_mode(i, mode="buy")
            elif self.data.iloc[i][f"{self.column}_signal"] == "sell":
                if self.flag is None:
                    self._init_mode(i, mode="sell")
                else:
                    self._write_value(i, mode="buy")
                    self._init_mode(i, mode="sell")
            else:
                continue
        self._cut_laststate()
        self.df_buy = pd.DataFrame(self.buy)
        self.df_sell = pd.DataFrame(self.sell)

    def visualize(self):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.data.index, y=self.data[self.column], mode="markers"))
        fig.add_trace(go.Scatter(x=self.df_buy["date"], y=self.df_buy["value"], mode="markers"))
        fig.add_trace(go.Scatter(x=self.df_sell["date"], y=self.df_sell["value"], mode="markers"))

        for i in range(len(self.df_buy)):
            date = self.df_buy.iloc[i]["date"]
            value = self.df_buy.iloc[i]["value"]
            fig.add_annotation(x=date, y=value, showarrow=True,
                               arrowhead=2, arrowcolor="red",
                               ax=0, ay=30, arrowwidth=2,
                               )
        for i in range(len(self.df_sell)):
            date = self.df_sell.iloc[i]["date"]
            value = self.df_sell.iloc[i]["value"]
            fig.add_annotation(x=date, y=value, showarrow=True,
                               arrowhead=2, arrowcolor="blue",
                               ax=0, ay=-30, arrowwidth=2)
        fig.update_layout(showlegend=True)
        fig.show()


class GoldenDeadCross(Strategy):
    def __init__(self, df, column, short, long):
        super().__init__(df, column)
        self.execute(short, long)
        self.backtest()

    def _algorithm(self, short, long):
        self.data = sma(self.data, self.column, [short, long])
        self.data = self.data.dropna()
        golden = self.data[f"{self.column}_sma{short}"] >= self.data[f"{self.column}_sma{long}"]
        self.data.loc[golden, f"{self.column}_state"] = 1
        self.data = self.data.fillna(0)

    def execute(self, short, long):
        self._algorithm(short, long)
        super().execute()

    def backtest(self):
        super().backtest()

    def visualize(self):
        super().visualize()




df = api.stock_ohlcv("삼성전자", "20010101", "20060101")
st1 = GoldenDeadCross(df, "종가", 20, 60)
st1.visualize()