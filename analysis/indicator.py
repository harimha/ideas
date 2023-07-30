from analysis.visualization.plotly_lib import Plot

class Indicator():

    @staticmethod
    def bollinger_band(df_raw, windows=20, upper_k=2, lower_k=2):
        df_indi = df_raw.copy()
        mean = df_indi["value"].rolling(windows).mean()
        std = df_indi["value"].rolling(windows).std()
        df_indi["mid"] = mean
        df_indi["upper"] = mean + upper_k * std
        df_indi["lower"] = mean - lower_k * std

        return df_indi

    @staticmethod
    def sma(df_raw, *windows):
        df_indi = df_raw.copy()
        for window in windows:
            df_indi[f"sma{window}"] = df_indi["value"].rolling(window).mean()

        return df_indi

    @staticmethod
    def visualize_indicator(indicator, *args, **kwargs):
        df_indi = indicator(*args, **kwargs)
        x = df_indi.index
        fig = Plot().init_fig()
        for column in df_indi.columns:
            fig = Plot().line_plot(fig, x=df_indi.index, y=df_indi[column], name=column, mark=True)

        Plot().fig_show(fig, name="indicator", html=True)


