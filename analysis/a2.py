'''
지표 성과 평가 지표
지표의 시그널 발생시점 이후 수익률에 대해서 .. 
MDD 
MDU
Mean return
기간은 ?
시그널은 양방향
기간 : 매수 시그널 ~ 매도 시그널
단기 시그널의 문제 
매매횟수 문제 

모든 기간에 대해서 2가지 state 존재
+sig , -sig
'''

import fdata.api as api
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

data = api.stock_c("삼성전자",sdate="20000101", edate="20080101")

# 골든크로스/데드크로스

def golden_dead_cross(data, short:int, long:int):
    df = data.copy()
    df.columns = ["일자", "종가"]
    df[f"ma_{short}"] = df["종가"].rolling(short).mean()
    df[f"ma_{long}"] = df["종가"].rolling(long).mean()
    df = df.dropna()

    golden = df[f"ma_{short}"] >= df[f"ma_{long}"]
    df.loc[golden, "state"] = 1
    df = df.fillna(0)
    buy_sig = ((df["state"] == 1) & (df["state"].shift(1) == 0))
    sell_sig = ((df["state"] == 0) & (df["state"].shift(1) == 1))
    df.loc[buy_sig, "signal"] = "buy"
    df.loc[sell_sig, "signal"] = "sell"
    df = df.fillna("hold")

    return df




# find MDD
gold = {"index":[], "max":[], "min":[], "mean":[]}
dead = {"index":[], "max":[], "min":[], "mean":[]}
data_lst = []
base_price = None
flag = None
for i in range(len(df)):
    if df.iloc[i]["switch"] =="-":
        if flag is None :
            pass
        else :
            data_lst.append(df.iloc[i]["종가"])
    elif df.iloc[i]["switch"] == "to_gold":
        if len(data_lst) > 0 :
            data_lst.append(df.iloc[i]["종가"])
            mean_price = sum(data_lst) / len(data_lst)
            max_price = max(data_lst)
            min_price = min(data_lst)
            dead["mean"].append((mean_price / base_price - 1))
            dead["max"].append((max_price / base_price - 1))
            dead["min"].append((min_price / base_price - 1))
            data_lst = []
            data_lst.append(df.iloc[i]["종가"])
            gold["index"].append(df.iloc[i]["일자"])
            base_price = df.iloc[i]["종가"]
            flag = df.iloc[i]["switch"]
        else:
            data_lst.append(df.iloc[i]["종가"])
            gold["index"].append(df.iloc[i]["일자"])
            base_price = df.iloc[i]["종가"]
            flag = df.iloc[i]["switch"]
    else:
        if len(data_lst) > 0 :
            data_lst.append(df.iloc[i]["종가"])
            mean_price = sum(data_lst)/len(data_lst)
            max_price = max(data_lst)
            min_price = min(data_lst)
            gold["mean"].append((mean_price/base_price-1))
            gold["max"].append((max_price/base_price-1))
            gold["min"].append((min_price/base_price-1))
            data_lst = []
            data_lst.append(df.iloc[i]["종가"])
            dead["index"].append(df.iloc[i]["일자"])
            base_price = df.iloc[i]["종가"]
            flag = df.iloc[i]["switch"]
        else:
            data_lst.append(df.iloc[i]["종가"])
            dead["index"].append(df.iloc[i]["일자"])
            base_price = df.iloc[i]["종가"]
            flag = df.iloc[i]["switch"]

    if i == (len(df)-1):
        if df.iloc[i]["sig"] == "golden":
            gold["index"].pop()

        elif df.iloc[i]["sig"] == "dead":
            dead["index"].pop()

df_golden = pd.DataFrame(gold)
df_golden.drop("index", axis=1, inplace=True)
df_golden.columns =["g_max", "g_min", "g_mean"]
df_dead = pd.DataFrame(dead)
df_dead.drop("index", axis=1, inplace=True)
df_dead.columns =["d_max", "d_min", "d_mean"]
df_golden.describe()
df_golden
df_golden_dead = pd.concat([df_golden, df_dead], axis=1)
df_golden_dead.tail()
df_golden_dead.apply(np.mean, axis=0)
df_golden_dead.apply(min, axis=0)
df_golden_dead.apply(max, axis=0)

df.iloc[0]





df = api.stock_c("삼성전자",sdate="20000101", edate="20230721")
df.columns = ["일자", "종가"]


# 골든크로스/데드크로스

df["ma_20"] = df["종가"].rolling(20).mean()
df["ma_60"] = df["종가"].rolling(60).mean()
df = df.dropna()
df.loc[df.index,"sig"] = "dead"
cond_golden = df["ma_20"]>=df["ma_60"]
df.loc[cond_golden, "sig"] = "golden"
# switch point
to_gold_switch_cond = ((df["sig"]=="golden") & (df["sig"].shift(1)=="dead"))
to_dead_switch_cond = ((df["sig"]=="dead") & (df["sig"].shift(1)=="golden"))
df.loc[to_gold_switch_cond, "switch"] = "to_gold"
df.loc[to_dead_switch_cond, "switch"] = "to_dead"
sns.set_theme()
plt.rc('font', family='Malgun Gothic')
sns.scatterplot(df, x="일자", y="종가", hue="switch")