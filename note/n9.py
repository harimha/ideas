import fdata.api as api
import pandas as pd
from analysis.visualization.plotly_lib import Plot
from analysis.indicator import ema, visualize_indicator
from sklearn.preprocessing import StandardScaler

df = api.kospi_sector_c()
df= df.dropna()


# 수익률 정의
# 30일 평균 수익률
for col in df.columns[1:]:
    df[f"{col}_d"] = df[col]/df[col].shift(1)-1

for col in df.columns[1:22]:
    df[f"{col}_r"] = df[f"{col}_d"].rolling(30).mean()
# df2 = df[df.columns[43:]]
df2 = df[df.columns[22:]]
df2 = df2.dropna()

# visualize
# fig = Plot().init_fig_y2()
# fig = Plot().line_plot(fig, mark=True, x=df2.index, y=df2["의약품_r"], name="의약품")
# fig = Plot().line_plot(fig, mark=True, x=df2.index, y=df2["제조업_r"], name="제조업")
# Plot().fig_show(fig, html=False)

df_eco= pd.read_csv("C:\\Users\\cceed\\Desktop\\동행지수.csv")
df_eco = df_eco.set_index("일자").rename(columns={'동행지수순환변동치':"value"})
df_eco["local_max"] = df_eco["value"].rolling(6).max()
df_eco["local_min"] = df_eco["value"].rolling(6).min()
con1 = df_eco["value"] == df_eco["local_min"]
con3 = df_eco["value"] == df_eco["local_max"]
df_eco.loc[(df_eco["value"]<100),"state"] = "침체"
df_eco.loc[(df_eco["value"]<100) & con3,"state"] = "회복"
df_eco.loc[(df_eco["value"]>=100),"state"] = "확장"
df_eco.loc[(df_eco["value"]>=100) & con1,"state"] = "수축"
df_eco = df_eco.dropna()
# size = df_eco.groupby("state").size()
# tot = df_eco.groupby("state").size().sum()
# df_tot = pd.DataFrame({"freq":size, "ratio":round(size/tot,2)})
# df_tot
# df_eco.loc[(df_eco["state"]=="침체"),"color"] = "blue"
# df_eco.loc[(df_eco["state"]=="회복"),"color"] = "orange"
# df_eco.loc[(df_eco["state"]=="확장"),"color"] = "red"
# df_eco.loc[(df_eco["state"]=="수축"),"color"] = "purple"

# visualize
# fig = Plot().init_fig()
# fig = Plot().scatter_plot(fig, df_eco.index, df_eco["value"], marker={"color":df_eco["color"]})
# Plot().fig_show(fig, html=False)

df_eco = df_eco.reset_index()
df_eco["일자"] = pd.to_datetime(df_eco["일자"])
df_eco["year"]=df_eco["일자"].dt.year
df_eco["month"]=df_eco["일자"].dt.month

df2_z = df2.copy()
df2_z = df2_z.reset_index()
df2_z["일자"] = pd.to_datetime(df2_z["일자"])
df2_z["year"]=df2_z["일자"].dt.year
df2_z["month"]=df2_z["일자"].dt.month

df_m = df2_z.merge(df_eco, on=['year', 'month'], how='left')
df_m = df_m.dropna()
df_m = df_m.set_index("일자_x")


# heatmap
# 산업섹터별로 경기변동에따라 평균수익률이 다름
df_test = df_m[['음식료품_d', '섬유의복_d', '종이목재_d', '화학_d', '의약품_d', '비금속광물_d', '철강금속_d',
       '기계_d', '전기전자_d', '의료정밀_d', '운수장비_d', '유통업_d', '전기가스업_d', '건설업_d',
       '운수창고업_d', '통신업_d', '금융업_d', '증권_d', '보험_d', '서비스업_d', '제조업_d',"state"]]

df_heat = round(df_test.groupby("state").mean()*100,4)
s1 = df_heat.loc["수축"].sort_values(ascending=False).head(5)
df_rank = pd.DataFrame({"수축":df_heat.loc["수축"].sort_values(ascending=False).head(5).index,
                        "확장":df_heat.loc["확장"].sort_values(ascending=False).head(5).index,
                        "침체":df_heat.loc["침체"].sort_values(ascending=False).head(5).index,
                        "회복":df_heat.loc["회복"].sort_values(ascending=False).head(5).index})
import plotly.express as px
fig = px.imshow(df_heat, x=df_heat.columns, y=df_heat.index)
fig.show()


#  분석
X = df_m[["음식료품_r", "섬유의복_r", "종이목재_r", "화학_r", "의약품_r",
      "비금속광물_r", "철강금속_r", "기계_r", "전기전자_r", "의료정밀_r",
      "운수장비_r", "유통업_r", "전기가스업_r", "건설업_r", "운수창고업_r",
      "통신업_r", "증권_r", "보험_r", "서비스업_r", "제조업_r"]]
y = df_m["state"]


# del df, df2
# del df2_z, df_eco, df_m

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
X_train, X_test, y_train, y_test = train_test_split(X, y , test_size=0.3)
rfc = RandomForestClassifier()

rfc.fit(X_train, y_train)

# 예측
y_pred_rfc = rfc.predict(X_test)
df_pred = pd.DataFrame({"y":y_test, "y_pred":y_pred_rfc}, index=y_test.index)

# 평가
rpt_rfc = classification_report(y_test, y_pred_rfc)
print(rpt_rfc)
# rfc.estimators_[0].tree_.max_depth



# 최근 데이터로 예측 해보기
df_last = pd.DataFrame({"value":df_m["value"], "state":df_m["state"]})
df_last.loc[df_last["state"]=="확장", "color"] = "red"
df_last.loc[df_last["state"]=="수축", "color"] = "purple"
df_last.loc[df_last["state"]=="침체", "color"] = "blue"
df_last.loc[df_last["state"]=="회복", "color"] = "orange"
df_last.loc[df_last["state"]=="확장", "state"] = 2
df_last.loc[df_last["state"]=="수축", "state"] = 1
df_last.loc[df_last["state"]=="침체", "state"] = -2
df_last.loc[df_last["state"]=="회복", "state"] = -1


df2_z = df2_z.set_index("일자")
X_test_recent = df2_z[["음식료품_r", "섬유의복_r", "종이목재_r", "화학_r", "의약품_r",
      "비금속광물_r", "철강금속_r", "기계_r", "전기전자_r", "의료정밀_r",
      "운수장비_r", "유통업_r", "전기가스업_r", "건설업_r", "운수창고업_r",
      "통신업_r", "증권_r", "보험_r", "서비스업_r", "제조업_r"]]
X_test_recent = X_test_recent.loc[X_test_recent.index>"2023-06-30"]
y_pred_recent = rfc.predict(X_test_recent)

y_df = pd.DataFrame({"y_pred_recent":y_pred_recent}, index=X_test_recent.index)
y_df.loc[y_df["y_pred_recent"]=="확장"] = 2
y_df.loc[y_df["y_pred_recent"]=="침체"] = -2
y_df.loc[y_df["y_pred_recent"]=="회복"] = 1
y_df.loc[y_df["y_pred_recent"]=="수축"] = -1


fig = Plot().init_fig_y2(rows=2,cols=1)
fig = Plot().scatter_plot(fig, marker={"color":df_last["color"]}, x=df_last.index, y=df_last["value"], name="value", rows=1,cols=1)
fig = Plot().line_plot(fig, mark=True, x=df_last.index, y=df_last["state"], name="state", rows=2,cols=1)
fig = Plot().line_plot(fig, mark=True, x=y_df.index, y=y_df["y_pred_recent"], name="state_prediction", rows=2,cols=1)
fig = Plot().xaxis_datetime_range_break(fig, df_last.index )
Plot().fig_show(fig, html=False)



