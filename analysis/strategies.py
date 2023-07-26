from analysis.indicator import sma
from plotly.subplots import make_subplots
from analysis.visualization import Visualize
from analysis.utils import Singleton
from abc import ABC, abstractmethod
import pandas as pd
import plotly.graph_objects as go



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


class GoldenDeadCross(Strategy, Visualize):
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


'''
algorithm
buy condition
sell condition

signal
buy signal
sell signal
hold signal

entry, exit
buy entry, buy exit
sell entry, sell exit

case 
buy 여러번 발생, sell 여러번 발생
개수 1개가 아닌 분할 매수 

4개의 signal
buy_entry
buy_exit
sell_entry
sell_exit

보유 잔고
수량, 단가

결과
청산수익


state
bull, bear, 
'''


