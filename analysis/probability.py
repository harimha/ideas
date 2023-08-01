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




# 지표 S를 가지고 정답 df_buy에 해당하는 값을 구분해 낼 수 있는지 classification 해보자
from sklearn.ensemble import RandomForestClassifier as RFC
from analysis.strategies import MACD

df = api.stock_ohlcv("삼성전자", "20100101", "20110101")
df = df[["종가","고가","저가"]].rename(columns={"종가":"value","고가":"high","저가":"low"})

df_buy = buy_point(df, 0.2, 0.1)
df_sell = sell_point(df, 0.2, 0.1)

strtg = MACD(df, "value")
df_indi = strtg.set_sub_indicators()
y = []
for i in range(len(df)):
    if df.index[i] in df_buy.index:
        y.append(True)
    else:
        y.append(False)
df["y"] = y

X = df_indi[["macd_20_60","ima_9"]]
y = df["y"]

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
rf = RFC()
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

df = pd.DataFrame({"y_true":y_test, "y_pred":y_pred})
from sklearn.metrics import classification_report, precision_score

rpt = classification_report(y_test, y_pred)

print(rpt)

# True 에 대해서 precision 은 모델이 True로 분류했을때,
# 실제 y%이상 하락하지 않으면서 x%이상 수익을 본 경우임
# 즉 x% * precision *100 은 support*precision만큼의 에 대해서 해당 수익 발생및 청산
# y%*(1-precision)*100에 support*(1-precision)만큼의 손실 발생 및 청산임
prec = precision_score(y_test, y_pred)
rtrn = 0.2*prec*24
loss = -0.1*(1-prec)*24
print(rtrn + loss)
# 이러한 전략에 대해서 백테스트 해보자



