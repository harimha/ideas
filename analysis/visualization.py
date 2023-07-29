from datetime import datetime
from pandas.api.types import is_list_like
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


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

    def fig_show(self, fig, name=None, html=True):
        if html:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            fig.write_html(f"html/{name}_{now}.html")
        else:
            fig.show()


class Plot(Figure):
    def scatter_plot(self, fig, x, y, name=None, marker: dict = None, row=1, col=1, y2=False):
        fig.add_trace(go.Scatter(x=x,
                                 y=y,
                                 mode="markers",
                                 marker=marker,
                                 name=name), row=row, col=col, secondary_y=y2)

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

    def bar_chart(self, fig, x, y, text, width, offset, color=None, name=None, rows=1, cols=1, y2=False):
        fig.add_trace(go.Bar(x=x,
                             y=y,
                             text=text,
                             name=name,
                             width=width,
                             offset=offset,
                             opacity=0.5,
                             textposition="outside",
                             textangle=0), row=rows, col=cols, secondary_y=y2)

        return fig
















