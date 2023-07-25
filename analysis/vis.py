import datetime

import plotly.express as px
import plotly.graph_objects as go
from analysis.strategies import GoldenDeadCross
import fdata.api as api
from plotly.subplots import make_subplots
import pandas as pd

df = api.stock_ohlcv("현대차", "20010101", "20230101")
st1 = GoldenDeadCross(df, "종가", 20, 60)

df = st1.data
df_buy = st1.df_buy
df_buy["state"] = "buy"
df_sell = st1.df_sell
df_sell["state"] = "sell"
df_m = pd.concat([df_buy, df_sell], axis=0)
df_m = df_m.sort_values("date")
df_m["cum_rtrn"] = df_m["rtrn"].cumsum()

buy_state = df["종가_state"]==1
sell_state = df["종가_state"]==0
df.loc[buy_state, "종가_state"] = "lightcoral"
df.loc[sell_state, "종가_state"] = "lightskyblue"


fig = make_subplots(specs=[[{"secondary_y": True}]])
# fig = make_subplots(rows=2, cols=1)
fig.add_trace(go.Scatter(x=df_m["date"],
                         y=df_m["cum_rtrn"],
                         mode="lines",
                         name="cum_rtrn"),
              # row=2, col=1,
              secondary_y=True)

bar_width = df_m["date"].shift(-1)-df_m["date"]
bar_width = bar_width.fillna(df.index[-1]-df_sell["date"].iloc[-1])
bar_width = bar_width.astype("int64")/1000000
bar_off = bar_width.astype("int64")/2000000

buy_state = df_m["state"]=="buy"
sell_state = df_m["state"]=="sell"
df_m.loc[buy_state, "state"] = "orange"
df_m.loc[sell_state, "state"] = "purple"
df_m["rtrn"] = round(df_m["rtrn"],2)


fig.add_trace(go.Scatter(x=df.index,
                         y=df["종가"],
                         mode="markers",
                         marker={"size":3,
                                 "opacity":0.5,
                                 "color": df["종가_state"]},
                         name="종가"),
# row=1, col=1,
                         secondary_y=False)

fig.add_trace(go.Scatter(x=df_buy["date"],
                         y=df_buy["value"],
                         mode="markers",
                         marker={"size": 4,
                                 "color": "red"},
                         name="buy"
                         ),
# row=1, col=1,
                         secondary_y=False)
fig.add_trace(go.Scatter(x=df_sell["date"],
                         y=df_sell["value"],
                         mode="markers",
                         marker={"size": 4,
                                 "color": "blue"},
                         name="sell"
                         ),
# row=1, col=1,
                         secondary_y=False)

# add annotation and arrow
for i in range(len(df_buy)):
    date = df_buy.iloc[i]["date"]
    value = df_buy.iloc[i]["value"]
    fig.add_annotation(x=date,
                       y=value,
                       showarrow=True,
                       arrowhead=2,
                       arrowcolor="red",
                       ax=0,
                       ay=25,
                       arrowwidth=1.5,
                       # row=1, col=1,
                       secondary_y=False
                       )
for i in range(len(df_sell)):
    date = df_sell.iloc[i]["date"]
    value = df_sell.iloc[i]["value"]
    fig.add_annotation(x=date,
                       y=value,
                       showarrow=True,
                       arrowhead=2,
                       arrowcolor="blue",
                       ax=0,
                       ay=-25,
                       arrowwidth=1.5,
                       # row=1, col=1,
                       secondary_y=False)

fig.add_trace(go.Bar(x=df_m["date"],
                     y=df_m["rtrn"],
                     marker={"color":df_m["state"]},
                     name="buy_rtrn",
                     opacity=0.4,
                     width=list(bar_width),
                     offset=bar_off,
                     text=df_m["rtrn"],
                     textposition="outside",
                     textangle=0),
              # row=2, col=1,
                     secondary_y=True)
#
# for i in range(len(df_m)):
#     date = df_m.iloc[i]["date"]
#     rtrn = df_m.iloc[i]["rtrn"]
#     fig.add_annotation(x=date,
#                        y=rtrn,
#                        text=rtrn,
#                        # row=1, col=1,
#                        secondary_y=True
#                        )
# fig.update_xaxes(range=[df.index[0], df.index[-1]])
# fig.update_xaxes(
#     dtick="M1",
#     tickformat="%b\n%Y")

fig.show()
