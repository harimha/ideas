import fdata.api as api
import pandas as pd
from analysis.strategies import GoldenDeadCross, BollingerBand
from analysis.indicator import sma, visualize_indicator
from analysis.visualization.plotly_lib import Plot
from datetime import datetime
import numpy as np


# parameter, strategy 마다 result 결과 통계적 데이터 셋 유지
# 이후 통계적으로 해당 데이터 분석
# 해당 전략의 유용성 metric 구성
# 결론 -> 해당 전략이 유효한지 아닌지 파악
# 유효하다면 어떤 metric?
# plotly 너무 느려서, matplotlib으로 다시 최적화
# data backtest 다시 최적화


# df = api.stock_ohlcv("삼성전자", "20000101", "20230701")
# df = df[["종가", "거래량"]]
# df = sma(df, "종가", 20)
# fig = visualize_indicator(sma, df, "종가", "거래량", 20)
# fig = Plot().xaxis_datetime_range_break(fig, df.index)
# Plot().fig_show(fig, html=False)

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


from analysis.strategies import UpTrend
df = api.stock_c("현대차", "20100101", "20130101")
upt = UpTrend(df, "현대차", rate=1.005)
df_indi = upt.set_sub_indicators()
df_cond = upt.get_condition_df(df_indi)
fig = Plot().init_fig()
fig = upt.vis_entry_exit_condition(fig, df_cond, vis_indi=True)
Plot().fig_show(fig, html=False)


# 가격 기준으로 차트를 보면 기울기, 각도의 모습이  가격이 올라감에 따라 왜곡되어보임
# log 가격 ?
# acc_return 기준?

df = api.stock_c("현대차", "20000101", "20130101")
df["rtrn"] = (df["현대차"]/df["현대차"].shift(1))-1
df["acc_rtrn"] = df["rtrn"].cumsum()
df["log_price"] = np.log10(df["현대차"])

upt = UpTrend(df, "acc_rtrn", rate=1.005)
df_indi = upt.set_sub_indicators()
df_cond = upt.get_condition_df(df_indi)
fig = Plot().init_fig()
fig = upt.vis_entry_exit_condition(fig, df_cond, vis_indi=True)
Plot().fig_show(fig, html=False)


# 보조지표에 대한 논리적 적용은 모두 같으나
# 단지 차트로 시각적으로 확인하기에 편리성을 위해 log값을 취해서 사용하는 것임

fig = Plot().init_fig_y2()
# fig = Plot().line_plot(fig, x=df.index, y=df["log_price"],name="log", mark=True, y2=True)
fig = Plot().line_plot(fig, x=df.index, y=df["acc_rtrn"],name="acc", mark=True, y2=True)
fig = Plot().line_plot(fig, x=df.index, y=df["현대차"],name="현대차", mark=True)
fig = Plot().xaxis_datetime_range_break(fig, df.index)
Plot().fig_show(fig, html=False)

# 가격은 지수적으로 변화한다.
# price_t = price_t_1*(1+rate_t_1)
# log(price)는 선형적으로 변화한다.
# ln(price_t) = ln(p_t_1)+ln(1+rate_t_1)


np.linspace(1,100,100)
fig = Plot().init_fig()
fig = Plot().line_plot(fig, x=np.linspace(1,100,100),
                       y=1.05**np.linspace(1,100,100),name="exp", mark=True)
fig = Plot().line_plot(fig, x=np.linspace(1,100,100),
                       y=np.linspace(1,100,100),name="line", mark=True)
Plot().fig_show(fig, html=False)
