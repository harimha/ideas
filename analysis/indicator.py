
'''
모든 지표는 2가지(매수,매도)상태를 가진다
두 상태에 대해서 metric의 비교를 통해 지표의 정확도를 평가한다.
'''
import pandas as pd
from analysis.strategies import golden_dead_cross
import fdata.api as api

data = api.stock_c("삼성전자", "20050101", "20230101")
df = golden_dead_cross(data, 20, 60)

# 성과 평가
# backtesting
# metrics

class Backtesting():
    pass


class Metrics():
    def __init__(self):
        pass

    def mdd(self, data):
        df = data.copy()
        state_sell = {"date": [], "mdd": []}
        state_buy = {"date": [], "mdd": []}
        data_lst = []
        base_price = None
        flag = None

        for i in range(len(df)):
            data_lst.append(df.iloc[i]["price"])
            if df.iloc[i]["signal"] == "buy":
                if flag is None:
                    data_lst = []
                    flag = df.iloc[i]["signal"]
                    state_buy["date"].append(df.iloc[i]["date"])
                    base_price = df.iloc[i]["price"]
                else:
                    flag = df.iloc[i]["signal"]
                    mdd = base_price / max(data_lst) - 1
                    state_sell["mdd"].append(mdd)

                    data_lst = []
                    state_buy["date"].append(df.iloc[i]["date"])
                    base_price = df.iloc[i]["price"]
            elif df.iloc[i]["signal"] == "sell":
                if flag is None:
                    data_lst = []
                    flag = df.iloc[i]["signal"]
                    state_sell["date"].append(df.iloc[i]["date"])
                    base_price = df.iloc[i]["price"]
                else:
                    flag = df.iloc[i]["signal"]
                    mdd = min(data_lst) / base_price - 1
                    state_buy["mdd"].append(mdd)

                    data_lst = []
                    state_sell["date"].append(df.iloc[i]["date"])
                    base_price = df.iloc[i]["price"]
            else:
                continue

        if df["state"][-1:].iloc[0]:
            state_buy["date"].pop()
        else:
            state_sell["date"].pop()

        df_buy = pd.DataFrame(state_buy)
        df_sell = pd.DataFrame(state_sell)

        buy_mdd = df_buy["mdd"].min()
        sell_mdd = df_sell["mdd"].min()
        print(f"buy_mdd : {round(buy_mdd,2)}\nsell_mdd : {round(sell_mdd,2)} ")

        return df_buy, df_sell, buy_mdd, sell_mdd


metrics = Metrics()
df_buy, df_sell, buy_mdd, sell_mdd  = metrics.mdd(df)

