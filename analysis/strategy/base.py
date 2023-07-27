import fdata.api as api
from pandas.api.types import is_list_like
import plotly.graph_objects as go
from datetime import datetime

class Analysis():
    def _set_rawdata(self, df, column):
        raw_data = df[[column]].copy()
        raw_data.columns = ["value"]

        return raw_data

class Indicators(Analysis):
    def sma(self, df, column, windows):
        df_indi = self._set_rawdata(df, column)
        if is_list_like(windows):
            for window in windows:
                df_indi[f"sma{window}"] = df_indi["value"].rolling(window).mean()
        else:
            df_indi[f"sma{windows}"] = df_indi["value"].rolling(windows).mean()

        return df_indi



class Visualization():
    def _fig_show(self, fig, name=None, html=True):
        if html:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            fig.write_html(f"{name}_{now}.html")
        else:
            fig.show()

    def visualize(self, df, columns:str or [], mode="markers", name=None, html=True):
        fig = go.Figure()
        if is_list_like(columns):
            for col in columns:
                fig.add_trace(go.Scatter(x=df.index,
                                         y=df[col],
                                         mode=mode))
        else:
            fig.add_trace(go.Scatter(x=df.index,
                                     y=df[col],
                                     mode=mode))
        self._fig_show(fig, name, html)


df = api.stock_c("삼성전자", "20200101", "20230101")
indi = Indicators()
df_indi = indi.sma(df,"삼성전자", [20,60])
vis =Visualization()
vis.visualize(df_indi, df_indi.columns, name="삼성전자", mode="lines+markers")

class SubIndicator():

    def set_sub_indicators(self):
        sub_indicators

    def add_sub_indicators(self, df, col_name):
        df_sub = df.copy()
        df_sub[col_name] = df

        return df_sub
    
    def add_sub_indicators(self, df, column):
        df_sub = df[[column]].copy()
        df_sub.columns = ["value"]
        df_sub["midline"] = df_sub[self.column].rolling(20).mean()
        df_sub["upper_bound"] = \
            df_sub[self.column].rolling(20).mean() + 2 * df_sub[self.column].rolling(20).std()
        df_sub["lower_bound"] = \
            df_sub[self.column].rolling(20).mean() - 2 * df_sub[self.column].rolling(20).std()

        return df_sub
    


class Algorithm():
    pass
