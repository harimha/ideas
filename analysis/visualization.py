from datetime import datetime
from pandas.api.types import is_list_like
import plotly.graph_objects as go

def _fig_show(fig, name=None, html=True):
    if html:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fig.write_html(f"html/{name}_{now}.html")
    else:
        fig.show()


def scatter_plot(fig, x, y, color=None, name=None, marker:dict=None, secondary_y=False):
    fig.add_trace(go.Scatter(x=x,
                             y=y,
                             mode="markers",
                             marker=marker,
                             name=name),
                             secondary_y=secondary_y)

    return fig

def line_plot(fig, x, y,
              color=None, name=None, mark=False, line:dict=None, marker:dict=None, secondary_y=False):
    if mark:
        fig.add_trace(go.Scatter(x=x,
                                 y=y,
                                 mode="lines+markers",
                                 marker=marker,
                                 line=line,
                                 name=name),
                                 secondary_y=secondary_y)
    else:
        fig.add_trace(go.Scatter(x=x,
                                 y=y,
                                 mode="lines",
                                 line=line,
                                 name=name),
                                 secondary_y=secondary_y)
    return fig



def visualize(df, columns:str or [], fig, mode="markers", name=None, html=True):
    if is_list_like(columns):
        for col in columns:
            fig.add_trace(go.Scatter(x=df.index,
                                     y=df[col],
                                     mode=mode,
                                     name=col))
    else:
        fig.add_trace(go.Scatter(x=df.index,
                                 y=df[columns],
                                 mode=mode,
                                 name=columns))
    return fig
