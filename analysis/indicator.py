from pandas.api.types import is_list_like


def sma(data, columns, windows):
    if is_list_like(columns):
        df = data[columns].copy()
        for col in columns:
            if is_list_like(windows):
                for window in windows:
                    df[f"{col}_sma{window}"] = df[col].rolling(window).mean()
            else:
                df[f"{col}_sma{windows}"] = df[col].rolling(windows).mean()
    else:
        df = data[[columns]].copy()
        if is_list_like(windows):
            for window in windows:
                df[f"{columns}_sma{window}"] = df[columns].rolling(window).mean()
        else:
            df[f"{columns}_sma{windows}"] = df[columns].rolling(windows).mean()

    return df


def ema(data, columns, window):
    '''
    지수이동평균(exponetial moving average)
    '''
    df = data[columns].copy()
    if is_list_like(columns):
        for col in columns:
            df[f"{col}_ema{window}"] = df[col].ewm(span=window).mean()
    else:
        df[f"{columns}_ema{window}"] = df[columns].ewm(span=window).mean()

    return df


def macd(data):
    pass



