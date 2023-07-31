import fdata.api as api
import pandas as pd
from analysis.strategies import GoldenDeadCross, BollingerBand
from analysis.visualization.plotly_lib import Plot
from datetime import datetime
import numpy as np
import random


def rtrn_score(count, sdate, edate, strategy, *args, **kwargs):
    '''
    rtrn 은 한번 매매 진입에 따른 (비용고려한)수익임
    rtrn을 누적적으로 더했을 때 모든 기간에서 하락없이 우상향 하는지가 제일 중요
    '''
    code_df = api.kospi_common_stock()["단축코드"]
    sample_n = random.sample(range(len(code_df)), count)
    code_df = code_df.loc[sample_n]
    i = 1
    df_rtrn = pd.DataFrame(columns=["entry_date", "rtrn"])
    for code in code_df:
        print(f"{i} / {len(code_df)}")
        i += 1
        try:
            name = api.scode_to_name(code)
            df = api.stock_c(name, sdate, edate)
            strtg = strategy(df, name, *args, **kwargs)
            df_backtest = strtg.backtest()
            df_backtest = df_backtest[["entry_date", "rtrn"]]
            df_rtrn = pd.concat([df_rtrn, df_backtest], axis=0)
        except:
            continue

    df_rtrn = df_rtrn.sort_values("entry_date")
    df_rtrn.index = range(len(df_rtrn))
    df_rtrn["acc_rtrn"] = df_rtrn["rtrn"].cumsum()

    fig = Plot().init_fig()
    fig = Plot().line_plot(fig, x=df_rtrn['entry_date'], y=df_rtrn["acc_rtrn"], mark=True)
    Plot().fig_show(fig, html=False)

    return df_rtrn, fig


# 상한가,하한가 종목은 매수,매도 불가능 한 것 고려

# BollingerBand(df_raw=, column=, windows=, upper_k=, lower_k=)
rtrn_df, = rtrn_score(100, "20220101", "20230101", BollingerBand, upper_k=4)
# rtrn_df, = rtrn_data(10, "20220101", "20230101", GoldenDeadCross)


