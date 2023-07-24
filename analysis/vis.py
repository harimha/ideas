
import plotly.express as px
import plotly.graph_objects as go


def stock_signal(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["price"], mode="markers"))
    fig.add_trace(go.Scatter(x=buy_df["date"], y=buy_df["price"], mode="markers"))
    fig.add_trace(go.Scatter(x=sell_df["date"], y=sell_df["price"], mode="markers"))
    for i in range(len(buy_df)):
        date = buy_df.iloc[i]["date"]
        price = buy_df.iloc[i]["price"]
        fig.add_annotation(x=date, y=price, showarrow=True,
                           arrowhead=2, arrowcolor="red",
                           ax=0, ay=30, arrowwidth=2,
                           )
    for i in range(len(sell_df)):
        date = sell_df.iloc[i]["date"]
        price = sell_df.iloc[i]["price"]
        fig.add_annotation(x=date, y=price, showarrow=True,
                           arrowhead=2, arrowcolor="blue",
                           ax=0, ay=-30, arrowwidth=2)
    fig.update_layout(showlegend=False)
    fig.show()
