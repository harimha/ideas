import fdata.api as api
import pandas as pd
from analysis.indicator import buy_point, sell_point
from analysis.visualization.plotly_lib import Plot
from analysis.strategies import MACD
import numpy as np
import random

# buy_point는 정답인 값이라고 보고 macd를 지표를 가지고 buy_point를 분류해 낼 수 있는지
# RandomForestClassifier로 분류해보고 분류 정확도 및 성과를 측정
# 학습용 데이터 셋 구축
def data_set(count, sdate, edate, max_rtrn=0.2, loss_cut=0.05):
    code_df = api.kospi_common_stock()["단축코드"]
    sample_n = random.sample(range(len(code_df)), count)
    code_df = code_df.loc[sample_n]
    count_number = 1
    data = pd.DataFrame()
    for code in code_df:
        print(f"{count_number} / {len(code_df)}")
        count_number += 1
        try:
            name = api.scode_to_name(code)
            df_hlc = api.stock_hlc(name, sdate, edate)
            df_buy = buy_point(df_hlc, max_rtrn, loss_cut)
            df_indi = MACD(df_buy, "value").set_sub_indicators()
        except:
            print(f"error {code}")
            continue

        df_buy = pd.concat([df_buy, df_indi[df_indi.columns[1:]]], axis=1)
        df_buy.reset_index(inplace=True)
        df_buy["stock_name"] = name
        data = pd.concat([data, df_buy], axis=0)
    data.index = range(len(data))
    data["buy"] = data["buy"].astype("bool")

    return data

data = data_set(10, "20020101", "20230101", max_rtrn=0.2, loss_cut=0.1)


from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, precision_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split

X = data[["macd_20_60", "ima_9"]]
y = data["buy"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
rfc = RandomForestClassifier(max_depth=50)
rfc.fit(X_train, y_train)
y_pred = rfc.predict(X_test)
rpt = classification_report(y_test, y_pred)
print(rpt)

y_df = pd.DataFrame({"y_true":y_test,"y_pred":y_pred}, index=y_test.index)
data_result = data.merge(y_df, left_index=True, right_index=True, how='inner')

precision_score_lst = {}

for stock_name in data_result["stock_name"].unique():
    data_stock_name = data.loc[data["stock_name"] == stock_name]
    true_result = data_result.loc[(data_result["stock_name"] == stock_name) &
                                  (data_result["y_pred"]==True) &
                                  (data_result["y_true"]==True), ["value"]]
    false_result = data_result.loc[(data_result["stock_name"] == stock_name) &
                                  (data_result["y_pred"]==True) &
                                  (data_result["y_true"]==False), ["value"]]

    precision_score_lst.update({stock_name:(round(len(true_result) / (len(true_result) + len(false_result)),3),len(true_result) + len(false_result))})


print(precision_score_lst)





fig = Plot().init_fig_y2()

stock_name ="SG글로벌"
data_stock_name = data.loc[data["stock_name"] == stock_name]
true_result = data_result.loc[(data_result["stock_name"] == stock_name) &
                              (data_result["y_pred"] == True) &
                              (data_result["y_true"] == True), ["value"]]
false_result = data_result.loc[(data_result["stock_name"] == stock_name) &
                               (data_result["y_pred"] == True) &
                               (data_result["y_true"] == False), ["value"]]
fig = Plot().line_plot(fig, x=data_stock_name.index, y=data_stock_name["value"], mark=True, name="value")
fig = Plot().scatter_plot(fig, x=true_result.index, y=true_result["value"], marker={"color":"red"}, name="true_result")
fig = Plot().scatter_plot(fig, x=false_result.index, y=false_result["value"], marker={"color":"blue"}, name="false_result")
Plot().fig_show(fig, html=False)

# 거래정지 종목의 잘못된 signal 발생으로 왜곡현상있음



#
# fig = Plot().init_fig_y2(rows = 5, cols = int(np.ceil(len(data_result["stock_name"].unique())/5)))
#
# for i, stock_name in enumerate(data_result["stock_name"].unique(), 1):
#     data_stock_name = data.loc[data["stock_name"] == stock_name]
#     true_result = data_result.loc[(data_result["stock_name"] == stock_name) &
#                                   (data_result["y_pred"] == True) &
#                                   (data_result["y_true"] == True), ["value"]]
#     false_result = data_result.loc[(data_result["stock_name"] == stock_name) &
#                                    (data_result["y_pred"] == True) &
#                                    (data_result["y_true"] == False), ["value"]]
#     rows = np.mod(i,5)+1
#     cols = int(np.ceil(i/5))
#     print(rows, cols)
#     fig = Plot().line_plot(fig, x=data_stock_name.index, y=data_stock_name["value"], mark=True, name="value", rows=rows, cols=cols)
#     fig = Plot().scatter_plot(fig, x=true_result.index, y=true_result["value"], marker={"color":"red"}, name="true_result", rows=rows, cols=cols)
#     fig = Plot().scatter_plot(fig, x=false_result.index, y=false_result["value"], marker={"color":"blue"}, name="false_result", rows=rows, cols=cols)
# Plot().fig_show(fig, html=False)
#



