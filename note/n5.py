import fdata.api as api
import pandas as pd
from analysis.indicator import visualize_indicator
from analysis.visualization.plotly_lib import Plot
df = api.kospi_sector_c()
df= df.dropna()

for i in range(len(df.columns)):
    df[f"{df.columns[i]}_r"] = df[df.columns[i]]/df[df.columns[i]].shift(30)-1
df2 = df[df.columns[22:]]

df2= df2.dropna()
from sklearn.preprocessing import StandardScaler
scalar = StandardScaler()

df2_z = scalar.fit_transform(df2)
df2_z = pd.DataFrame(df2_z, columns=df2.columns, index=df2.index)

fig = Plot().init_fig()
for i in range(len(df2_z.columns)):
    fig = Plot().line_plot(fig, x=df2_z.index, y=df2_z[df2_z.columns[i]], name=df2_z.columns[i])
Plot().fig_show(fig, html=False)


