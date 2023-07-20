import fdata.db.api as db
import fdata.api as api
import matplotlib.pyplot as plt

# 급등 t일 전의 주가 특성은 무엇일까?
df = api.stock_c("에이스침대",sdate="20000101", edate="20230721")
df = df.set_index("일자")

for i in range(1,31,1):
    df[f"t+{i}"] = df["에이스침대"].shift(-i)

df = df.dropna()
for i in range(1, 31, 1):
    df[f"수익률t+{i}"] = df[f"t+{i}"]/df["에이스침대"]-1


df.to_csv("test.csv",encoding="cp949")


# 볼린져밴드 상단 돌파 시점 (t) 이후 수익률 추이
# 20일, std 2.5




# 볼린져 밴드 상단 돌파 후 눌림목 매매
