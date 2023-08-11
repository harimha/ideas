from datetime import datetime
from pandas.api.types import is_list_like
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd


class Figure():
    def _secondary_y_specification(self, rows=1, cols=1, coordinate: list = [(1, 1)]):
        specs = np.full((rows, cols), {"secondary_y": False})
        specs = specs.tolist()

        for r, c in coordinate:
            specs[r - 1][c - 1] = {"secondary_y": True}


        return specs

    def _set_background_color(self, fig, color):
        fig.update_layout(plot_bgcolor=color)

        return fig

    def init_fig(self, rows=1, cols=1, specs=None):
        fig = make_subplots(rows=rows, cols=cols, specs=specs)
        fig = self._set_background_color(fig, "white")
        fig.update_xaxes(gridcolor="lightgray")
        fig.update_yaxes(gridcolor="lightgray")

        return fig

    def init_fig_y2(self, rows=1, cols=1,
                    shared_xaxes=True, vertical_spacing=0.02, horizontal_spacing=0.1, y2_coordinate: list = [(1, 1)]):
        specs = self._secondary_y_specification(rows, cols, y2_coordinate)
        fig = make_subplots(rows=rows, cols=cols,
                            shared_xaxes=shared_xaxes,
                            vertical_spacing=vertical_spacing,
                            horizontal_spacing=horizontal_spacing,
                            specs=specs)
        fig = self._set_background_color(fig, "white")
        fig.update_xaxes(gridcolor="lightgray")
        fig.update_yaxes(gridcolor="lightgray")

        return fig

    def xaxis_datetime_range_break(self, fig, dt_series):
        dt_all = pd.date_range(start=dt_series[0], end=dt_series[-1])
        dt_breaks = [day for day in dt_all if not day in dt_series]
        fig.update_xaxes(
            rangebreaks=[dict(values=dt_breaks)]
        )

        return fig

    def fig_show(self, fig, name=None, html=True):
        if html:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            fig.write_html(f"analysis/plot/{name}_{now}.html")
        else:
            fig.show()

    def get_color_df(self, df, column, value_color: dict):
        '''
        color 변환용 값 반환
        value_color : ex){"buy": "orange", "sell": "purple"}
        '''
        df_col = df.copy()
        for value, color in value_color.items():
            df_col.loc[df_col[column] == value, "color"] = color
        df_col = df_col["color"]

        return df_col


class Plot(Figure):
    def scatter_plot(self, fig, x, y, name=None, marker: dict = None, rows=1, cols=1, y2=False):
        fig.add_trace(go.Scatter(x=x,
                                 y=y,
                                 mode="markers",
                                 marker=marker,
                                 name=name), row=rows, col=cols, secondary_y=y2)

        return fig

    def line_plot(self, fig, x, y, name=None, mark=False, line: dict = None,
                  marker: dict = None, rows=1, cols=1, y2=False):
        if mark:
            fig.add_trace(go.Scatter(x=x,
                                     y=y,
                                     mode="lines+markers",
                                     marker=marker,
                                     line=line,
                                     name=name), row=rows, col=cols, secondary_y=y2)
        else:
            fig.add_trace(go.Scatter(x=x,
                                     y=y,
                                     mode="lines",
                                     line=line,
                                     name=name), row=rows, col=cols, secondary_y=y2)

        return fig

    def bar_chart(self, fig, x, y, text=None, width=None, offset=None, color=None, name=None, rows=1, cols=1, y2=False):
        fig.add_trace(go.Bar(x=x,
                             y=y,
                             text=text,
                             name=name,
                             width=width,
                             offset=offset,
                             opacity=0.5,
                             textposition="outside",
                             marker=dict(color=color),
                             textangle=0), row=rows, col=cols, secondary_y=y2)

        return fig


    def histogram(self, fig, x, nbins=None, prob=False, cumulative=False, name=None, rows=1, cols=1, y2=False):
        if prob:
            prob = "probability"
        else:
            prob = None
        fig.add_trace(go.Histogram(x=x,
                                   xbins=nbins,
                                   name=name,
                                   histnorm=prob,
                                   cumulative={"direction": "increasing",
                                               "enabled": cumulative}),
                      row=rows,
                      col=cols,
                      secondary_y=y2)

        return fig
















