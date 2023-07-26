import pandas as pd
import fdata.api as api
import plotly.graph_objects as go
from abc import ABC, abstractmethod


class TestAlgo(ABC):
    def __init__(self, data, column):
        self.raw_data = data[[column]].copy()
        self.data = data[[column]].copy()
        self.column = column

    @abstractmethod
    def _set_sub_indicators(self):
        pass

    @abstractmethod
    def _set_conditions(self):
        pass

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
        self.data["position"] = positions

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
            value = self.data.iloc[i][self.column]
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

    def algorithm_result(self) -> pd.DataFrame:
        self.data = self.raw_data.copy()
        self._set_sub_indicators()
        self._set_conditions()
        self._set_positions()
        self._set_trading_signals()
        df_result = self.data

        return df_result

    def visualize_algo(self):
        self.algorithm_result()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.data.index,
                                 y=self.data[self.column],
                                 mode="markers",
                                 marker={"size": 3, "opacity": 0.5}))
        fig.add_trace(go.Scatter(x=self.data[self.data["position"] == "long"].index,
                                 y=self.data[self.data["position"] == "long"][self.column],
                                 mode="markers",
                                 name="long",
                                 marker={"size": 3, "opacity": 0.5}))
        fig.add_trace(go.Scatter(x=self.data[self.data["position"] == "short"].index,
                                 y=self.data[self.data["position"] == "short"][self.column],
                                 mode="markers",
                                 name="short",
                                 marker={"size": 3, "opacity": 0.5}))
        self._vis_trading_signal(fig)
        fig.show()


class BollingerBandTest(TestAlgo):
    def __init__(self, data, column):
        super().__init__(data, column)

    def _set_sub_indicators(self):
        self.data["midline"] = self.data[self.column].rolling(20).mean()
        self.data["upper_bound"] = \
            self.data[self.column].rolling(20).mean() + 2 * self.data[self.column].rolling(20).std()
        self.data["lower_bound"] = \
            self.data[self.column].rolling(20).mean() - 2 * self.data[self.column].rolling(20).std()
        self.data.dropna(inplace=True)

    def _set_conditions(self):
        self.data["entry_buy_cond"] = self.data[self.column] >= self.data["upper_bound"]
        self.data["entry_sell_cond"] = self.data[self.column] <= self.data["lower_bound"]
        self.data["exit_buy_cond"] = self.data[self.column] <= self.data["midline"]
        self.data["exit_sell_cond"] = self.data[self.column] > self.data["midline"]


'''

개별종목
portfolio
pair

Strategy
    algorithm
        condition
            entry_buy
            entry_sell
            exit_buy
            exit_sell
        trading
            entry_buy
            entry_sell
            exit_buy
            exit_sell
        position
            long - buy_entry to buy_exit
            short - sell_entry to sell_exit 
            nothing - exit to entry

        backtest
            trading setting
                entry config 
                    entry only first signal
                    entry all signal
                    entry only satisfy condition
                    entry limit counts
                exit config

            result_paper
                date, state(buy, sell), entry_price, exit_price, amount, return

            score
                mdd
                acc_return


            accounts
                base_amounts
                acc_rtrn
                amounts    


'''

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


보유 잔고
수량, 단가

결과
청산수익


state
bull, bear, 
'''

