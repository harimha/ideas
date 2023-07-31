import fdata.api as api
import pandas as pd
from analysis.strategies import GoldenDeadCross, BollingerBand
from analysis.visualization.plotly_lib import Plot
from datetime import datetime
import numpy as np
import random


def rtrn_data(amount, sdate, edate):
    df_stock = api.stock_name("KOSPI")
    sample_n = random.sample(range(len(df_stock)), amount)
    df_stock = df_stock.loc[sample_n]
    i = 1
    df_rtrn = pd.DataFrame(columns=["entry_date", "rtrn"])
    for name in df_stock:
        print(f"{i} / {len(df_stock)}")
        i += 1
        try:
            df = api.stock_c(name, sdate, edate)
            gdc = BollingerBand(df, name)
            df_backtest = gdc.backtest()
            df_backtest = df_backtest[["entry_date", "rtrn"]]
            df_rtrn = pd.concat([df_rtrn, df_backtest], axis=0)
        except:
            continue

    df_rtrn = df_rtrn.sort_values("entry_date")
    df_rtrn.index = range(len(df_rtrn))

    return df_rtrn

def compare_accrtrn(number, sdate, edate):
    df_stock = api.stock_name("KOSPI")
    sample_n = random.sample(range(len(df_stock)), number)
    df_stock = df_stock.loc[sample_n]
    fig = Plot().init_fig()
    i = 1
    result=[]
    for name in df_stock:
        print(f"{i} / {len(df_stock)}")
        i += 1
        try:
            df = api.stock_c(name, sdate, edate)
            gdc = BollingerBand(df,name)
            df_backtest = gdc.backtest()
            df_r = df_backtest[["entry_date", "acc_rtrn"]]
            result.append(df_r["acc_rtrn"].iloc[-1])
            fig = Plot().line_plot(fig, x=df_r["entry_date"], y=df_r["acc_rtrn"], name=name)
        except:
            continue
    return fig, result

def vis_backtest_stock(stock_name, sdate, edate):
    fig = Plot().init_fig_y2()
    df = api.stock_c(stock_name, sdate, edate)
    gdc = BollingerBand(df, stock_name)
    df_algo = gdc.execute_algorithm()
    df_backtest = gdc.backtest()
    fig = gdc.vis_backtest(fig, df_algo, df_backtest)
    Plot().fig_show(fig, html=False)


# fig , result = compare_accrtrn(100, "20200101", "20230731")
# Plot().fig_show(fig, html=False)

# vis_backtest_stock("노루홀딩스우", "20200101", "20230731")

df_rtrn = rtrn_data(500, "20200101", "20230731")
df_rtrn["acc_rtrn"] = df_rtrn["rtrn"].cumsum()
fig = Plot().init_fig_y2()
fig = Plot().line_plot(fig, x=df_rtrn["entry_date"],y=df_rtrn["acc_rtrn"])
Plot().fig_show(fig, html=False)
# return 분석
# df = pd.DataFrame({"rtrn":rtrn})
# std = np.std(df.rtrn, ddof=1)
# avg = np.mean(df.rtrn)
# df["rtrn"] = df.loc[df["rtrn"]<(avg+5*std)]
# df.index = range(len(df))
# df["cumsum"] = df.cumsum()
# fig = Plot().init_fig()
# fig = Plot().line_plot(fig, x=df.index, y=df["cumsum"])
# Plot().fig_show(fig, html=False)

# import plotly.express as px
# fig = px.histogram(x=rtrn, nbins=50)
# fig.show()
# fig = px.box(y=rtrn)
# fig.show()




# 무작위 선정
# 기간마다 특성이 다르니까 기간별로 강건한지
# rtrn 은 한번 매매 진입에 따른 수익임
# rtrn을 모두 더했을때 +의 정도
# 개수가 많아질수록 rtrn이 선형적으로 증가하는지
# 상한가,하한가 종목은 매수,매도 불가능 한 것 고려
# 거래량, 거래대금 조건도 추가
# 우선주 제외 



# parameter, strategy 마다 result 결과 통계적 데이터 셋 유지
# 이후 통계적으로 해당 데이터 분석
# 해당 전략의 유용성 metric 구성
# 결론 -> 해당 전략이 유효한지 아닌지 파악
# 유효하다면 어떤 metric?
# plotly 너무 느려서, matplotlib으로 다시 최적화
# data backtest 다시 최적화

