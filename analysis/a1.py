import fdata.api as api
import matplotlib.pyplot as plt
df = api.stock_c("삼성전자","20000101","20230808")
df = df.set_index("일자")



'''
골든크로스
단기 이동평균선이 장기 이동평균선을 상향 돌파
이론 : 골든크로스 발생시 매수신호 -> 골든 크로스 발생시 매수하면 수익 가능성 높음
-> 골든 크로스 발생시 주가 상승 확률 높음

측정 : 
골든 크로스 발생 후 30일간의 평균 주식 수익률 측정
골든 크로스 발생 후 30일간의 최대 주식 수익률 측정
골든 크로스 발생 후 30일간의 최소 주식 수익률 측정

'''

# 골든 크로스 신호
df["ma_20"] = df["삼성전자"].rolling(20).mean()
df["ma_60"] = df["삼성전자"].rolling(60).mean()
df["20-60"] = df["ma_20"]-df["ma_60"]
df = df.dropna()
df["golden"] = 0
golden_cond = ((df["20-60"]*df["20-60"].shift(1)<0) & (df["20-60"]>df["20-60"].shift(1)))
df["golden"][golden_cond] = 1

# t시점의 t+30간의 최대,최소,평균 수익률 측정
max_list = []
min_list = []
avg_list = []
for i in range(len(df)):
    max_list.append(df["삼성전자"].iloc[i:30+i].max())
    min_list.append(df["삼성전자"].iloc[i:30+i].min())
    avg_list.append(df["삼성전자"].iloc[i:30+i].mean())

df["max"] = max_list
df["min"] = min_list
df["avg"] = avg_list
df["max_r"] = df["max"]/df["삼성전자"]-1
df["min_r"] = df["min"]/df["삼성전자"]-1
df["avg_r"] = df["avg"]/df["삼성전자"]-1


df.groupby("golden")["max_r"].mean()[1]
df.groupby("golden")["min_r"].mean()[1]
df.groupby("golden")["avg_r"].mean()

df.groupby("golden")["avg_r"].unique()[1]



df.to_csv("test.csv", encoding="cp949")


''' 
타이밍 매매 
매수 타이밍, 매도 타이밍
가장 적절한 매수 타이밍
가장 적절한 매도 타이밍
어떻게 정의하고
어떻게 문제를 해결할까
'''