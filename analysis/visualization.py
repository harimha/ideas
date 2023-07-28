from datetime import datetime
from pandas.api.types import is_list_like
import plotly.graph_objects as go

def _fig_show(fig, name=None, html=True):
    if html:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fig.write_html(f"html/{name}_{now}.html")
    else:
        fig.show()

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
