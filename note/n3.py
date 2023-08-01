import fdata.api as api
import pandas as pd
from analysis.strategies import GoldenDeadCross, BollingerBand
from analysis.indicator import sma, visualize_indicator, ema, estd, std, macd
from analysis.visualization.plotly_lib import Plot
from datetime import datetime
import numpy as np


## 찾고자 하는 것
# p -> q 명제 에서 q를 True로 하는 p를 찾고자 한다.
# 여기서 q는 매수를하면 보유기간동안 최대손실 y%이내에서 비용을 제하고 x%이상의 수익이 나는가? 라는 명제이고
# q를 true로 하는 충분조건에 해당하는 p(지표 등)을 찾고자 한다.
# q를 만족하는 모든 상황을 정의하고 q 를 만족하는 상황 이전의 데이터를 가지고 예측할 수 있는지 찾고자 한다.
# q를 더 엄밀히 정의하면 비용을 제한 수익이 x%이상이 나오는 매수지점, 투자 기간은 상관없음, 매수한 가격대비
# y%이상 하락하지 않음
# 여기서 q는 매수 지점을 의미

# 매도지점 q는
# q를 더 엄밀히 정의하면 비용을 제한 수익이 x%이상이 나오는 매도지점, 투자 기간은 상관없음, 매수한 가격대비
# y%이상 상승하지 않음

# q 조건 정의
# cost =  0.0023
def buy_point(df, target_rtrn=0.2, loss_cut=0.05):
    df = df.replace(0, None)
    df.dropna(inplace=True)
    cost = 0.0023
    entry_date = []
    entry_price = []
    duration = []
    for i in range(len(df)-1):
        buy_price = df.iloc[i]["value"]
        for j in range(1, len(df)-i):
            # 우선순위는 high_rtrn
            rtrn = (df.iloc[i + j]["high"] / buy_price - 1) - 0.0023
            loss_rtrn = (df.iloc[i + j]["low"] / buy_price - 1) - 0.0023
            if rtrn > target_rtrn:
                entry_date.append(df.index[i])
                entry_price.append(buy_price)
                duration.append(j)
                break
            if loss_rtrn < -loss_cut:
                break

    df_buy = pd.DataFrame({"entry_price":entry_price,
                            "duration":duration},
                          index= entry_date)
    return df_buy

def sell_point(df, target_rtrn=0.2, loss_cut=0.05):
    df = df.replace(0, None)
    df.dropna(inplace=True)
    cost = 0.0023
    entry_date = []
    entry_price = []
    duration = []
    for i in range(len(df)-1):
        sell_price = df.iloc[i]["value"]
        for j in range(1, len(df)-i):
            # 우선순위는 low_rtrn
            rtrn = (sell_price/df.iloc[i + j]["low"] - 1) - 0.0023
            loss_rtrn = (sell_price/df.iloc[i + j]["high"] - 1) - 0.0023
            if rtrn > target_rtrn:
                entry_date.append(df.index[i])
                entry_price.append(sell_price)
                duration.append(j)
                break
            if loss_rtrn < -loss_cut:
                break

    df_sell = pd.DataFrame({"entry_price":entry_price,
                            "duration":duration},
                          index=entry_date)

    return df_sell

def vis_buy_sell_point(fig, df, df_buy, df_sell, rows=1, cols=1):
    fig = Plot().line_plot(fig, x=df.index, y=df["value"], mark=True, name="value", rows=rows, cols=cols)
    fig = Plot().scatter_plot(fig, x=df_buy.index, y=df_buy["entry_price"], name="entry_buy", rows=rows, cols=cols)
    fig = Plot().scatter_plot(fig, x=df_sell.index, y=df_sell["entry_price"], name="entry_sell", rows=rows, cols=cols)

    return fig

df = api.stock_ohlcv("노루홀딩스우", "20000101", "20230101")
df = df[["종가","고가","저가"]].rename(columns={"종가":"value","고가":"high","저가":"low"})

df_buy = buy_point(df, 0.2, 0.03)
df_sell = sell_point(df, 0.2, 0.03)
# df = np.log(df)
# df_buy = np.log(df_buy)
# df_sell = np.log(df_sell)




df_macd = macd(np.log(df), "value", 20, 60)
df_macd2 = df_macd[["macd_20_60"]]
df_macd_macd = macd(df_macd2, "macd_20_60", 1, 9)

fig = Plot().init_fig_y2(2,1)
fig = vis_buy_sell_point(fig, df, df_buy, df_sell)
fig = Plot().line_plot(fig, x=df_macd.index, y=df_macd["ema20"], name="ema20", rows=1, cols=1)
fig = Plot().line_plot(fig, x=df_macd.index, y=df_macd["ema60"], name="ema60", rows=1, cols=1)
# fig = Plot().bar_chart(fig, x=df_macd.index, y=df_macd["macd_20_60"], name="macd_20_60", rows=2, cols=1)
fig = Plot().line_plot(fig, x=df_macd.index, y=df_macd["macd_20_60"], mark=True, name="macd_20_60", rows=2, cols=1)
fig = Plot().line_plot(fig, x=df_macd.index, y=df_macd["ima_9"], mark=True, name="ima_9", rows=2, cols=1)
fig = Plot().bar_chart(fig, x=df_macd_macd.index, y=df_macd_macd["macd_1_9"], name="macd_1_9", rows=2, cols=1)
fig = Plot().xaxis_datetime_range_break(fig, df.index)
Plot().fig_show(fig, html=False)


from analysis.strategies import Strategy

class N1(Strategy):
    def __init__(self, df_raw=None, column=None, short=20, long=60, ima=9, ema=True):
        super().__init__(df_raw, column, short=short, long=long, ima=ima, ema=ema)

    def set_params(self, short, long, ima, ema):
        '''
        이후 파라미터 변경시 활용하는 용도
        '''
        super().set_params(short=short, long=long, ima=ima, ema=ema)

    def set_sub_indicators(self):
        df_indi = macd(np.log(self.df_raw), self.column, **self.params)
        df_indi = df_indi[["value", f"macd_{self.params['short']}_{self.params['long']}", "ima_9"]]
        df_indi["value"] = self.df_raw["value"]
        df_indi.dropna(inplace=True)

        return df_indi


    def _entry_buy_condition(self, df_indi):

        cond1 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"] >= df_indi["ima_9"]
        cond2 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1) < df_indi["ima_9"].shift(1)
        cond3 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1)<=-0.1
        cond = cond1 & cond2 & cond3

        return cond

    def _entry_sell_condition(self, df_indi):
        cond1 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"] <= df_indi["ima_9"]
        cond2 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1) > df_indi["ima_9"].shift(1)
        cond3 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1)>=0.1
        cond = cond1 & cond2 & cond3
        return cond

    def _exit_buy_condition(self, df_indi):
        cond1 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"] <= df_indi["ima_9"]
        cond2 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1) > df_indi["ima_9"].shift(1)
        cond3 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1) >= 0.1
        cond = cond1 & cond2 & cond3
        return cond

    def _exit_sell_condition(self, df_indi):
        cond1 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"] >= df_indi["ima_9"]
        cond2 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1) < df_indi["ima_9"].shift(1)
        cond3 = df_indi[f"macd_{self.params['short']}_{self.params['long']}"].shift(1) <= -0.1
        cond = cond1 & cond2 & cond3
        return cond

# 이제 문제는
# q 를 true로 하는 p를 찾는 것이 과제
import fdata.api as api
import pandas as pd
from analysis.strategies import GoldenDeadCross, BollingerBand
from analysis.indicator import sma, visualize_indicator, ema, estd, std, macd
from analysis.visualization.plotly_lib import Plot
from datetime import datetime
import numpy as np

df = api.stock_ohlcv("노루홀딩스우", "20000101", "20230101")
df = df[["종가","고가","저가"]].rename(columns={"종가":"value","고가":"high","저가":"low"})
strtg = N1(df, "value")
df_indi =strtg.set_sub_indicators()
df_cond = strtg.get_condition_df(df_indi)
df_algo = strtg.execute_algorithm()
df_back = strtg.backtest()
df_back.head()

fig = Plot().init_fig_y2()
# fig = Plot().line_plot(fig, x=df_indi.index, y=df_indi["value"], rows=1, cols=1)
# fig = Plot().line_plot(fig, x=df_indi.index, y=df_indi["macd_20_60"], rows=2, cols=1)
# fig = Plot().line_plot(fig, x=df_indi.index, y=df_indi["ima_9"], rows=2, cols=1)
# fig = strtg.vis_entry_exit_condition(fig, df_cond, vis_indi=False)
fig = strtg.vis_algo(fig, df_algo, vis_indi=False)
Plot().fig_show(fig, html=False)