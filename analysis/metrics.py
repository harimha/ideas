import fdata.api as api
import pandas as pd
from analysis.strategies import GoldenDeadCross, BollingerBand
from analysis.visualization.plotly_lib import Plot
from datetime import datetime

# 모든 종목에 대해 청산 수익 rtrn에 대한 통계적 검증
# date, rtrn

# mdd

def rtrn_data(amount):
    df_stock = api.stock_name("KOSPI").iloc[:amount]
    i = 1
    rtrn = []
    for name in df_stock:
        print(f"{i} / {len(df_stock)}")
        i += 1
        try:
            df = api.stock_c(name, "20070101", "20090101")
            gdc = BollingerBand(df, name)
            df_backtest = gdc.backtest()
            rtrn_back = list(df_backtest["rtrn"])
            rtrn += rtrn_back
        except:
            continue
    return rtrn




rtrn = rtrn_data(200)
df = pd.DataFrame({"rtrn":rtrn})
df["cumsum"] = df.cumsum()
fig = Plot().init_fig()
fig = Plot().line_plot(fig, x=df.index, y=df["cumsum"])
Plot().fig_show(fig, html=False)

len(rtrn)
sum(rtrn)

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



# parameter, strategy 마다 result 결과 통계적 데이터 셋 유지
# 이후 통계적으로 해당 데이터 분석
# 해당 전략의 유용성 metric 구성
# 결론 -> 해당 전략이 유효한지 아닌지 파악
# 유효하다면 어떤 metric?
# plotly 너무 느려서, matplotlib으로 다시 최적화
# data backtest 다시 최적화

