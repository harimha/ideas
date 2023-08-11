import pandas as pd
from analysis.indicator import ema, visualize_indicator
# df_cpi= pd.read_csv("C:\\Users\\cceed\\Desktop\\cpi.csv")
# df_cpi = df_cpi.set_index("일자").rename(columns={'전년동기대비(%)':"cpi"})
df_eco= pd.read_csv("C:\\Users\\cceed\\Desktop\\동행지수.csv")
df_eco = df_eco.set_index("일자").rename(columns={'동행지수순환변동치':"economic"})
df_eco = ema(df_eco, "economic", 24)
df_eco.loc[(df_eco["value"]<100) & (df_eco["value"]<df_eco["ema24"]),"state"] = "침체"
df_eco.loc[(df_eco["value"]<100) & (df_eco["value"]>df_eco["ema24"]),"state"] = "회복"
df_eco.loc[(df_eco["value"]>=100) & (df_eco["value"]<df_eco["ema24"]),"state"] = "수축"
df_eco.loc[(df_eco["value"]>=100) & (df_eco["value"]>=df_eco["ema24"]),"state"] = "확장"



from analysis.visualization.plotly_lib import Plot

import plotly.express as px
fig = px.line(df_eco, y="value", color="state")

fig.show()


fig = Plot().init_fig()
fig = visualize_indicator(ema, df_eco, "economic",[],24)
Plot().fig_show(fig, html=False)