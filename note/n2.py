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
df = api.stock_c("현대차", "20050101", "20130101")
upt = UpTrend(df, "현대차", rate=1.005)
df_indi = upt.set_sub_indicators()
df_cond = upt.get_condition_df(df_indi)
fig = Plot().init_fig()
fig = upt.vis_entry_exit_condition(fig, df_cond, vis_indi=False)
Plot().fig_show(fig, html=False)


