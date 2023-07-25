from pandas.api.types import is_list_like


def sma(data, column, windows):
    df = data[[column]].copy()
    if is_list_like(windows):
        for window in windows:
            df[f"{column}_sma{window}"] = df[column].rolling(window).mean()
    else:
        df[f"{column}_sma{windows}"] = df[column].rolling(windows).mean()

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



