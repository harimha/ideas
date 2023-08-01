import pandas as pd
from analysis.visualization.plotly_lib import Plot

def bollinger_band(df_raw, value_column, windows=20, upper_k=2, lower_k=2):
    df_indi = df_raw.copy().rename(columns={value_column:"value"})
    mean = df_indi["value"].rolling(windows).mean()
    std = df_indi["value"].rolling(windows).std()
    df_indi["mid"] = mean
    df_indi["upper"] = mean + upper_k * std
    df_indi["lower"] = mean - lower_k * std

    return df_indi

def ema(df_raw, value_column, *windows):
    df_indi = df_raw.copy().rename(columns={value_column:"value"})
    for window in windows:
        df_indi[f"ema{window}"] = df_indi["value"].ewm(span=window).mean()

    return df_indi

def macd(df_raw, value_column, short=20, long=60, ima=9, ema=True):
    if ema:
        df_indi = df_raw.copy().rename(columns={value_column: "value"})
        df_indi[f"ema{short}"] = df_indi["value"].ewm(span=short).mean()
        df_indi[f"ema{long}"] = df_indi["value"].ewm(span=long).mean()
        df_indi[f"macd_{short}_{long}"] = df_indi[f"ema{short}"]-df_indi[f"ema{long}"]
        df_indi[f"ima_{ima}"] = df_indi[f"macd_{short}_{long}"].ewm(span=ima).mean()
    else:
        df_indi = df_raw.copy().rename(columns={value_column: "value"})
        df_indi[f"sma{short}"] = df_indi["value"].rolling(window=short).mean()
        df_indi[f"sma{long}"] = df_indi["value"].rolling(window=long).mean()
        df_indi[f"macd_{short}_{long}"] = df_indi[f"sma{short}"] - df_indi[f"sma{long}"]
        df_indi[f"ima_{ima}"] = df_indi[f"macd_{short}_{long}"].rolling(window=ima).mean()

    return df_indi


def std(df_raw, value_column, *windows):
    df_indi = df_raw.copy().rename(columns={value_column:"value"})
    for window in windows:
        df_indi[f"std{window}"] = df_indi["value"].rolling(window).std()

    return df_indi

def estd(df_raw, value_column, *windows):
    df_indi = df_raw.copy().rename(columns={value_column:"value"})
    for window in windows:
        df_indi[f"estd{window}"] = df_indi["value"].ewm(span=window).std()

    return df_indi

def sma(df_raw, value_column, *windows):
    df_indi = df_raw.copy().rename(columns={value_column:"value"})
    for window in windows:
        df_indi[f"sma{window}"] = df_indi["value"].rolling(window).mean()

    return df_indi

def up_trend(df_raw, value_column, rate=1.005):
    df_indi = df_raw.copy().rename(columns={value_column:"value"})

    indi = [df_indi["value"].iloc[0]]
    for i in range(1, len(df_indi)):
        if df_indi["value"].iloc[i] >= indi[i - 1] * rate:
            indi.append(indi[i - 1] * rate)
        else:
            indi.append(df_indi["value"].iloc[i])
    df_indi["indi"] = indi
    df_indi.loc[df_indi["indi"] != df_indi["value"], "indi2"] = True
    df_indi.fillna(False, inplace=True)

    return df_indi

def visualize_indicator(indicator, df_raw, value_column, y2_cols=[], *args, **kwargs):
    df_indi = indicator(df_raw, value_column, *args, **kwargs)
    x = df_indi.index
    fig = Plot().init_fig_y2()
    for column in df_indi.columns:
        if column in y2_cols:
            fig = Plot().bar_chart(fig, x=df_indi.index, y=df_indi[column], name=column, color="lightskyblue",y2=True)
        else:
            fig = Plot().line_plot(fig, x=df_indi.index, y=df_indi[column], name=column, mark=True, y2=False)

    return fig

