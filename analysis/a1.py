import fdata.db.api as db
import fdata.api as api
import matplotlib.pyplot as plt
import pandas as pd

df = api.stock_c("삼성전자",sdate="20000101", edate="20230721")
df = df.set_index("일자")

for i in range(1,31,1):
    df[f"t-{i}"] = df["삼성전자"].shift(i)

df = df.dropna()
for i in range(1,30,1):
    df[f"t-{i}r"] = df[f"t-{i}"]/df["t-30"]-1

df2 = df[["삼성전자"]].copy()
for i in range(1,31,1):
    df2[f"t+{i}"] = df2["삼성전자"].shift(-i)
df2 = df2.dropna()

max_val = df2.apply(max, axis=1)
min_val = df2.apply(min, axis=1)

df3 = pd.DataFrame({"close":df2["삼성전자"], "max":max_val, "min":min_val})
df3["max_r"] = df3["max"]/df3["close"]-1
df3["min_r"] = df3["min"]/df3["close"]-1
df3["score"] = df3["max_r"]+df3["min_r"]

df.head()
df_m = df.join(df3["score"])
df_m = df_m.dropna()
df_m.columns
X = df_m.iloc[:,31:-1]
y = df_m["score"]
price = df_m[["삼성전자"]]

del min_val
del max_val
del df
del df2
del df3
del df_m

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor as RFR
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True)

# x_train = X.iloc[:int(0.8*len(X))]
# x_test = X.iloc[int(0.8*len(X)):]
# y_train = y.iloc[:int(0.8*len(y))]
# y_test = y.iloc[int(0.8*len(y)):]


rfr = RFR()
rfr.fit(x_train, y_train)

# train data fit
rfr.score(x_train, y_train)
pred_y = rfr.predict(x_train)
df_fit = pd.DataFrame({"y":y_train, "y_hat":pred_y})
df_fit.to_csv("test4.csv",encoding="cp949")


# test data fit
rfr.score(x_test, y_test)
pred_y = rfr.predict(x_test)
df_fit = pd.DataFrame({"y":y_test, "y_hat":pred_y})
df_fit.to_csv("test4.csv",encoding="cp949")
df_price = price.join(df_fit)
df_price.fillna(0)
df_price.to_csv("test4.csv",encoding="cp949")



df.to_csv("test.csv",encoding="cp949")
df2.to_csv("test2.csv",encoding="cp949")
df_fit.to_csv("test4.csv",encoding="cp949")


# 볼린져 밴드 상단 돌파 후 눌림목 매매
