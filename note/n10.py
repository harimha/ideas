import fdata.api as api
import pandas as pd
from analysis.visualization.plotly_lib import Plot
from analysis.indicator import ema, visualize_indicator
from sklearn.preprocessing import StandardScaler

df = api.kospi_sector_c()
df= df.dropna()

# 수익률 정의
# 30일 수익률
for col in df.columns[1:]:
    df[f"{col}_r"] = df[col]/df[col].shift(30)-1

df2 = df[df.columns[22:]]
df2 = df2.dropna()

# visualize
# fig = Plot().init_fig_y2()
# fig = Plot().line_plot(fig, mark=True, x=df2.index, y=df2["의약품_r"], name="의약품")
# fig = Plot().line_plot(fig, mark=True, x=df2.index, y=df2["제조업_r"], name="제조업")
# # fig = Plot().line_plot(fig, mark=True, x=df2.index, y=df2["전기전자_r"], name="전기전자")
# Plot().fig_show(fig, html=False)

# df_eco 정의
df_eco= pd.read_csv("C:\\Users\\cceed\\Desktop\\동행지수.csv")
df_eco = df_eco.set_index("일자").rename(columns={'동행지수순환변동치':"value"})
df_eco["local_max"] = df_eco["value"].rolling(3).max()
df_eco["local_min"] = df_eco["value"].rolling(3).min()
con1 = df_eco["value"] == df_eco["local_min"]
con3 = df_eco["value"] == df_eco["local_max"]
df_eco.loc[(df_eco["value"]<100),"state"] = "침체"
df_eco.loc[(df_eco["value"]<100) & con3,"state"] = "회복"
df_eco.loc[(df_eco["value"]>=100),"state"] = "호황"
df_eco.loc[(df_eco["value"]>=100) & con1,"state"] = "후퇴"
df_eco = df_eco.dropna()
df_eco = df_eco.loc[df_eco.index>="20000101"]

# 비율 정의
size = df_eco.groupby("state").size()
tot = df_eco.groupby("state").size().sum()
df_tot = pd.DataFrame({"freq":size, "ratio":round(size/tot,2)})
df_tot

df_eco.loc[(df_eco["state"]=="침체"),"color"] = "blue"
df_eco.loc[(df_eco["state"]=="회복"),"color"] = "orange"
df_eco.loc[(df_eco["state"]=="호황"),"color"] = "red"
df_eco.loc[(df_eco["state"]=="후퇴"),"color"] = "purple"

# visualize
# fig = Plot().init_fig()
# fig = Plot().scatter_plot(fig, df_eco.index, df_eco["value"], marker={"color":df_eco["color"]})
# fig = Plot().line_plot(fig, df_eco.index, y=[100]*len(df_eco))
# fig.update_layout(title='경기동행지수 순환변동치', title_x=0.5)
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
# df_test = df_m[['음식료품_r', '섬유의복_r', '종이목재_r', '화학_r', '의약품_r', '비금속광물_r', '철강금속_r',
#        '기계_r', '전기전자_r', '의료정밀_r', '운수장비_r', '유통업_r', '전기가스업_r', '건설업_r',
#        '운수창고업_r', '통신업_r', '금융업_r', '증권_r', '보험_r', '서비스업_r', '제조업_r',"state"]]
# df_test.columns = ['음식료품', '섬유의복', '종이목재', '화학', '의약품', '비금속광물', '철강금속',
#        '기계', '전기전자', '의료정밀', '운수장비', '유통업', '전기가스업', '건설업',
#        '운수창고업', '통신업', '금융업', '증권', '보험', '서비스업', '제조업',"state"]
#
# df_heat = round(df_test.groupby("state").mean(),2)
# df_heat.loc["후퇴"].mean()
# df_heat.loc["호황"].mean()
# df_heat.loc["침체"].mean()
# df_heat.loc["회복"].mean()
#
# df_rank_head = pd.DataFrame()
# df_rank_tail = pd.DataFrame()
# for st in ["호황", "후퇴", "침체", "회복"]:
#     r_lst_head = []
#     r_lst_tail = []
#     for i in df_heat.loc[st].sort_values(ascending=False).head(5).index:
#         r_lst_head.append((i,df_heat.loc[st].sort_values(ascending=False).head(5).loc[i]))
#     for i in df_heat.loc[st].sort_values(ascending=True).head(5).index:
#         r_lst_tail.append((i,df_heat.loc[st].sort_values(ascending=True).head(5).loc[i]))
#     df_rank_head[st] = r_lst_head
#     df_rank_tail[st] = r_lst_tail
#
# df_rank_head.index.name = "rank"
# df_rank_tail.index.name = "rank"
# df_rank_head.index = range(1,6)
# df_rank_tail.index = range(1,6)
# df_rank_head
# df_rank_tail

#
# import plotly.express as px
# fig = px.imshow(df_heat, x=df_heat.columns, y=df_heat.index)
# fig.show()


#  분석
X = df_m[["음식료품_r", "섬유의복_r", "종이목재_r", "화학_r", "의약품_r",
      "비금속광물_r", "철강금속_r", "기계_r", "전기전자_r", "의료정밀_r",
      "운수장비_r", "유통업_r", "전기가스업_r", "건설업_r", "운수창고업_r",
      "통신업_r", "증권_r", "보험_r", "서비스업_r", "제조업_r"]]
y = df_m["state"]

X.index.name="일자"
X.head()
# del df, df2
# del df2_z, df_eco, df_m

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
X_train, X_test, y_train, y_test = train_test_split(X, y , test_size=0.3, random_state=2023)
rfc = RandomForestClassifier(random_state=2023, n_estimators=100, max_depth=None)

rfc.fit(X_train, y_train)

# 예측
y_pred_rfc = rfc.predict(X_test)


# 평가
rpt_rfc = classification_report(y_test, y_pred_rfc)
print(rpt_rfc)
# rfc.estimators_[0].tree_.max_depth


# 최근 데이터로 예측 해보기
X_test_recent = df2[["음식료품_r", "섬유의복_r", "종이목재_r", "화학_r", "의약품_r",
      "비금속광물_r", "철강금속_r", "기계_r", "전기전자_r", "의료정밀_r",
      "운수장비_r", "유통업_r", "전기가스업_r", "건설업_r", "운수창고업_r",
      "통신업_r", "증권_r", "보험_r", "서비스업_r", "제조업_r"]]
# X_test_recent = X_test_recent.loc[X_test_recent.index>"2023-06-30"]
X_test_recent = X_test_recent.loc[X_test_recent.index>"2021-01-30"]
y_pred_recent = rfc.predict(X_test_recent)
y_scores = rfc.predict_proba(X_test_recent)


df_score = pd.DataFrame(y_scores, index=X_test_recent.index)
df_score["state"] = y_pred_recent
df_score.columns = ["후퇴", "침체", "호황", "회복", "state"]

y_df = pd.DataFrame({"y_pred_recent":y_pred_recent}, index=X_test_recent.index)
df_last = pd.DataFrame({"value":df_m["value"], "state":df_m["state"]})

fig = Plot().init_fig_y2(cols=1, rows=2)
fig = Plot().line_plot(fig, mark=True, x=df_last.index, y=df_last["state"], name="state", cols=1, rows=1)
fig = Plot().line_plot(fig, mark=True, x=y_df.index, y=y_df["y_pred_recent"], name="state_prediction", cols=1, rows=1)

fig = Plot().line_plot(fig, mark=True, x=df_score.index, y=df_score["후퇴"], name="후퇴", cols=1, rows=2)
fig = Plot().line_plot(fig, mark=True, x=df_score.index, y=df_score["침체"], name="침체", cols=1, rows=2)
fig = Plot().line_plot(fig, mark=True, x=df_score.index, y=df_score["호황"], name="호황", cols=1, rows=2)
fig = Plot().line_plot(fig, mark=True, x=df_score.index, y=df_score["회복"], name="회복", cols=1, rows=2)

fig = Plot().xaxis_datetime_range_break(fig, df_last.index)
category_order = ['침체', '회복', '후퇴', '호황']  # 원하는 순서로 변경
fig.update_layout(yaxis={'categoryorder': 'array', 'categoryarray': category_order})

Plot().fig_show(fig, html=False)

df_last = pd.DataFrame({"value":df_m["value"], "state":df_m["state"]})
df_last.loc[df_last["state"]=="호황", "color"] = "red"
df_last.loc[df_last["state"]=="후퇴", "color"] = "purple"
df_last.loc[df_last["state"]=="침체", "color"] = "blue"
df_last.loc[df_last["state"]=="회복", "color"] = "orange"
df_last.loc[df_last["state"]=="호황", "state"] = 1
df_last.loc[df_last["state"]=="후퇴", "state"] = 0.5
df_last.loc[df_last["state"]=="침체", "state"] = -1
df_last.loc[df_last["state"]=="회복", "state"] = -0.5

df_last.head()
df_kospi = api.kospi_c("20010101","20230811")
df_kospi =df_kospi.set_index("일자")


fig = Plot().init_fig_y2(rows=2,cols=1)
fig = Plot().line_plot(fig, mark=True, x=df_kospi.index, y=df_kospi["종가"], name="kospi", rows=1,cols=1, y2=True)
fig = Plot().scatter_plot(fig, marker={"color":df_last["color"]}, x=df_last.index, y=df_last["value"], name="value", rows=1,cols=1)
fig = Plot().line_plot(fig, mark=True, x=df_last.index, y=df_last["state"], name="state", rows=2,cols=1)
fig = Plot().line_plot(fig, mark=True, x=y_df.index, y=y_df["y_pred_recent"], name="state_prediction", rows=2,cols=1)
fig = Plot().xaxis_datetime_range_break(fig, df_last.index )
Plot().fig_show(fig, html=False)



