

def golden_dead_cross(data, short:int, long:int):
    '''
    골든 크로스 : 단기 이평선이 장기 이평선을 상향 돌파, 매수 신호
    데드 크로스 : 단기 이평선이 장기 이평선을 하향 돌파, 매도 신호
    '''
    df = data.copy()
    df.columns = ["date", "price"]
    df[f"ma_{short}"] = df["price"].rolling(short).mean()
    df[f"ma_{long}"] = df["price"].rolling(long).mean()
    df = df.dropna()

    golden = df[f"ma_{short}"] >= df[f"ma_{long}"]
    df.loc[golden, "state"] = 1
    df = df.fillna(0)
    buy_sig = ((df["state"] == 1) & (df["state"].shift(1) == 0))
    sell_sig = ((df["state"] == 0) & (df["state"].shift(1) == 1))
    df.loc[buy_sig, "signal"] = "buy"
    df.loc[sell_sig, "signal"] = "sell"
    df = df.fillna("hold")
    df.index = range(len(df))

    return df


# macd

# stochastic
