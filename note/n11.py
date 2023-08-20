import fdata.api as api
import pandas as pd
from analysis.visualization.plotly_lib import Plot
from analysis.indicator import ema, visualize_indicator
from sklearn.preprocessing import StandardScaler
import numpy as np


fig =Plot().init_fig()
x = np.linspace(0, 4 * np.pi, 500)
y = np.sin(x)+100
y2 = 1/2*np.sin(x)+100
fig = Plot().line_plot(fig, x=x, y=y, name="경기동행지수")
fig = Plot().line_plot(fig, x=x, y=y2, name="경기동행지수(정책집행)")
Plot().fig_show(fig, html=False)

# 레이아웃 설정
layout = go.Layout(title='Sin Function', xaxis=dict(title='x'), yaxis=dict(title='sin(x)'))

# 그래프 생성 및 표시
fig = go.Figure(data=[trace], layout=layout)
fig.show()
np.linspace()
x = np.sin(np.pi/180)