class Backtest():
    def __init__(self):
        pass

def backtest(data, func):
    df = func()
    data_lst = []
    base_price = None
    flag = None
    state_sell = {"date": [], "price": [], "rtrn": [], "max_rtrn": [], "min_rtrn": []}
    state_buy = {"date": [], "price": [],"rtrn": [], "max_rtrn": [], "min_rtrn": []}
    for i in range(len(df)):
        data_lst.append(df.iloc[i]["price"])
        if df.iloc[i]["signal"] == "buy":
            if flag is None:
                data_lst = []
                flag = df.iloc[i]["signal"]
                base_price = df.iloc[i]["price"]
                state_buy["date"].append(df.iloc[i]["date"])
                state_buy["price"].append(base_price)
            else:
                max_rtrn = base_price / min(data_lst) - 1
                min_rtrn = base_price / max(data_lst) - 1
                re = base_price/df.iloc[i]["price"]- 1
                state_sell["rtrn"].append(re)
                state_sell["max_rtrn"].append(max_rtrn)
                state_sell["min_rtrn"].append(min_rtrn)

                data_lst = []
                flag = df.iloc[i]["signal"]
                base_price = df.iloc[i]["price"]
                state_buy["date"].append(df.iloc[i]["date"])
                state_buy["price"].append(base_price)

        elif df.iloc[i]["signal"] == "sell":
            if flag is None:
                data_lst = []
                flag = df.iloc[i]["signal"]
                base_price = df.iloc[i]["price"]
                state_sell["date"].append(df.iloc[i]["date"])
                state_sell["price"].append(base_price)

            else:
                max_rtrn = max(data_lst)/base_price -1
                min_rtrn = min(data_lst)/base_price -1
                re = df.iloc[i]["price"]/base_price - 1
                state_buy["rtrn"].append(re)
                state_buy["max_rtrn"].append(max_rtrn)
                state_buy["min_rtrn"].append(min_rtrn)

                data_lst = []
                flag = df.iloc[i]["signal"]
                base_price = df.iloc[i]["price"]
                state_sell["date"].append(df.iloc[i]["date"])
                state_sell["price"].append(base_price)
        else:
            continue

    if df["state"][-1:].iloc[0]:
        state_buy["date"].pop()
        state_buy["price"].pop()
    else:
        state_sell["date"].pop()
        state_sell["price"].pop()

    df_buy = pd.DataFrame(state_buy)
    df_sell = pd.DataFrame(state_sell)

    return df_buy, df_sell





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