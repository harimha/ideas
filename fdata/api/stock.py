import fdata.db.api as db

def stock_name(market="KOSPI"):
    obj = db.stock.StockCode()
    df = obj.read_db(obj.columns)
    df = df.loc[df["market_eng_name"]==market, "stock_name"]
    df.index = range(len(df))

    return df

def stock_per(stock_name, sdate=None, edate=None):
    obj = db.stock.StockPER_PBR_DIV()
    df = obj.read_db(stock_name, obj.columns, sdate, edate)

    return df

def stock_ohlcv(stock_name, sdate=None, edate=None):
    obj = db.stock.StockOHLCV_NAVER()
    df= obj.read_db(stock_name, obj.columns, sdate, edate)
    df = df.set_index("일자")

    return df

def stock_c(stock_name, sdate=None, edate=None):
    obj = db.stock.StockOHLCV_NAVER()
    df= obj.read_db(stock_name, ["일자", "종가"], sdate, edate)
    df.columns = ["date", stock_name]
    df= df.set_index("date")

    return df

def stock_v(stock_name, sdate=None, edate=None):
    obj = db.stock.StockOHLCV_NAVER()
    df= obj.read_db(stock_name, ["일자", "거래량"], sdate, edate)
    df.columns = ["일자", stock_name]

    return df



