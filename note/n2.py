import fdata.api as api
import pandas as pd
from analysis.strategies import GoldenDeadCross, BollingerBand
from analysis.indicator import sma, visualize_indicator, ema, estd, std
from analysis.visualization.plotly_lib import Plot
from datetime import datetime
import numpy as np

# df = api.stock_c("현대차", "20100101", "20230701")
# df = df.rename(columns={"현대차":"value"})
# df = np.log10(df)
# bb =BollingerBand(df, "현대차", )


# parameter, strategy 마다 result 결과 통계적 데이터 셋 유지
# 이후 통계적으로 해당 데이터 분석
# 해당 전략의 유용성 metric 구성
# 결론 -> 해당 전략이 유효한지 아닌지 파악
# 유효하다면 어떤 metric?
# plotly 너무 느려서, matplotlib으로 다시 최적화
# data backtest 다시 최적화

#
df = api.stock_c("현대차", "20100101", "20230701")
df = np.log10(df)
df = ema(df, "현대차", 20)
df = std(df, "value", 20)
df["upper"] = df["ema20"]+2*df["std20"]
df["lower"] = df["ema20"]-2*df["std20"]
df.dropna(inplace=True)

fig = Plot().init_fig()
fig = Plot().line_plot(fig, x=df.index, y=df["value"], name="value")
fig = Plot().line_plot(fig, x=df.index, y=df["ema20"], name="ema20")
fig = Plot().line_plot(fig, x=df.index, y=df["upper"], name="upper")
fig = Plot().line_plot(fig, x=df.index, y=df["lower"], name="lower")
fig = Plot().xaxis_datetime_range_break(fig, df.index)
Plot().fig_show(fig)



# 동적으로 window 사이즈를 변화시키는 mean, std를 구하고 볼린져밴드를 만든다
# 방향전환시 하향추세는 local max부터 시작, 상승추세는 local min 부터 시작
# 방향전환은 반대쪽 볼린저밴드를 돌파했을 때 부터 반대방향으로 인식하고 계산
# 초기값
# 선형으로 인식하기 위해 log사용

df = api.stock_c("현대차", "20100101", "20230701")
df = df.rename(columns={"현대차":"value"})
# df = np.log10(df)
# 초기화 변수
position = "nothing"
count = 0
val = []
mean_lst = []
std_lst = []
upper_lst = []
lower_lst = []
position_lst = []

for i in range(len(df)):
    data = df.iloc[i]["value"]
    # 초기화
    if position == "nothing":
        val.append(data)
        count +=1 # val에 담긴 데이터 개수
        if count >= 20:
            # mean = np.mean(val)
            mean = pd.DataFrame(val).ewm(span=len(val)).mean().iloc[-1][0]
            std = np.std(val)
            upper = mean + 1.5 * std
            lower = mean - 1.5 * std
            if data >=upper:
                position = "long"
                local_min= min(val[-20:])
                index = val.index(local_min)
                val = val[index:]
                count = len(val)
                mean = pd.DataFrame(val).ewm(span=len(val)).mean().iloc[-1][0]
                std = np.std(val)
                upper = mean + 1.5 * std
                lower = mean - 1.5 * std
                mean_lst.append(mean)
                std_lst.append(std)
                upper_lst.append(upper)
                lower_lst.append(lower)
                position_lst.append(position)
                continue
            elif data <= lower:
                position = "short"
                local_max = max(val[-20:])
                index = val.index(local_max)
                val = val[index:]
                count = len(val)
                mean = pd.DataFrame(val).ewm(span=len(val)).mean().iloc[-1][0]
                std = np.std(val, ddof=1)
                upper = mean + 1.5 * std
                lower = mean - 1.5 * std
                mean_lst.append(mean)
                std_lst.append(std)
                upper_lst.append(upper)
                position_lst.append(position)
                continue
        else:
            mean = None
            std = None
            upper = None
            lower = None

    # 초기화 이후
    if position == "long":
        val.append(data)
        count +=1 # val에 담긴 데이터 개수
        if data <= lower:
            position = "short"
            if count >= 20:
                local_max = max(val[-20:])
            else:
                local_max = max(val)
            index = val.index(local_max)
            val = val[index:]
            mean = pd.DataFrame(val).ewm(span=len(val)).mean().iloc[-1][0]
            std = np.std(val)
            upper = mean + 1.5 * std
            lower = mean - 1.5 * std
            mean_lst.append(mean)
            std_lst.append(std)
            upper_lst.append(upper)
            lower_lst.append(lower)
            position_lst.append(position)

            continue

        else:
            mean = pd.DataFrame(val).ewm(span=len(val)).mean().iloc[-1][0]
            std = np.std(val)
            upper = mean + 1.5 * std
            lower = mean - 1.5 * std

    if position == "short":
        val.append(data)
        count +=1 # val에 담긴 데이터 개수
        if data >= upper:
            position = "long"
            if count >= 20:
                local_min = min(val[-20:])
            else:
                local_min = min(val)
            index = val.index(local_min)
            val = val[index:]
            mean = pd.DataFrame(val).ewm(span=len(val)).mean().iloc[-1][0]
            std = np.std(val)
            upper = mean + 1.5 * std
            lower = mean - 1.5 * std
        else:
            mean = pd.DataFrame(val).ewm(span=len(val)).mean().iloc[-1][0]
            std = np.std(val)
            upper = mean + 1.5 * std
            lower = mean - 1.5 * std
            mean_lst.append(mean)
            std_lst.append(std)
            upper_lst.append(upper)
            lower_lst.append(lower)
            position_lst.append(position)

            continue

    mean_lst.append(mean)
    std_lst.append(std)
    upper_lst.append(upper)
    lower_lst.append(lower)
    position_lst.append(position)

df["mean"] = mean_lst
df["std"] = std_lst
df["upper"] = upper_lst
df["lower"] = lower_lst
df["position"] = position_lst
df = df.dropna()



fig = Plot().init_fig()
fig = Plot().line_plot(fig, x=df.index, y=df["value"], name="value")
fig = Plot().line_plot(fig, x=df.index, y=df["mean"], name="mean")
fig = Plot().line_plot(fig, x=df.index, y=df["upper"], name="upper")
fig = Plot().line_plot(fig, x=df.index, y=df["lower"], name="lower")
Plot().fig_show(fig)



# 꾸준한 상승장을 정의해보자
# 이동평균선이 꺾일 때 까지
# gdc = GoldenDeadCross()
# df_indi = gdc.set_sub_indicators()
# df_cond = gdc.get_condition_df(df_indi)
# df_cond.head()
# fig = Plot().init_fig()
# fig = gdc.vis_entry_exit_condition(fig, df_cond)
# Plot().fig_show(fig, html=False)

# 목표 상황을 정의하자
# 종가 기준으로 1%씩 상승시킨 지점보다 계속 위로 상승하는 경우 -> 찾고자 하는 상승장

#
# from analysis.strategies import UpTrend
# df = api.stock_c("현대차", "20100101", "20130101")
# upt = UpTrend(df, "현대차", rate=1.005)
# df_indi = upt.set_sub_indicators()
# df_cond = upt.get_condition_df(df_indi)
# fig = Plot().init_fig()
# fig = upt.vis_entry_exit_condition(fig, df_cond, vis_indi=True)
# Plot().fig_show(fig)


# 가격 기준으로 차트를 보면 기울기, 각도의 모습이  가격이 올라감에 따라 왜곡되어보임
# log 가격 ?
# acc_return 기준?

# df = api.stock_c("현대차", "20000101", "20130101")
# df["rtrn"] = (df["현대차"]/df["현대차"].shift(1))-1
# df["acc_rtrn"] = df["rtrn"].cumsum()
# df["log_price"] = np.log10(df["현대차"])







#
# upt = UpTrend(df, "acc_rtrn", rate=1.005)
# df_indi = upt.set_sub_indicators()
# df_cond = upt.get_condition_df(df_indi)
# fig = Plot().init_fig()
# fig = upt.vis_entry_exit_condition(fig, df_cond, vis_indi=True)
# Plot().fig_show(fig, html=False)


# 보조지표에 대한 논리적 적용은 모두 같으나
# 단지 차트로 시각적으로 확인하기에 편리성을 위해 log값을 취해서 사용하는 것임
#
# fig = Plot().init_fig_y2()
# # fig = Plot().line_plot(fig, x=df.index, y=df["log_price"],name="log", mark=True, y2=True)
# fig = Plot().line_plot(fig, x=df.index, y=df["acc_rtrn"],name="acc", mark=True, y2=True)
# fig = Plot().line_plot(fig, x=df.index, y=df["현대차"],name="현대차", mark=True)
# fig = Plot().xaxis_datetime_range_break(fig, df.index)
# Plot().fig_show(fig, html=False)

# 가격은 지수적으로 변화한다.
# price_t = price_t_1*(1+rate_t_1)
# log(price)는 선형적으로 변화한다.
# ln(price_t) = ln(p_t_1)+ln(1+rate_t_1)

#
# np.linspace(1,100,100)
# fig = Plot().init_fig()
# fig = Plot().line_plot(fig, x=np.linspace(1,100,100),
#                        y=1.05**np.linspace(1,100,100),name="exp", mark=True)
# fig = Plot().line_plot(fig, x=np.linspace(1,100,100),
#                        y=np.linspace(1,100,100),name="line", mark=True)
# Plot().fig_show(fig, html=False)
