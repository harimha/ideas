import fdata.db.api as db

def stock_hlm(stock_name, sdate=None, edate=None):
    '''
    고가, 저가, middle price
    '''
    obj = db.stock.StockOHLCV_NAVER()
    df = obj.read_db(stock_name, ["일자", "고가", "저가"], sdate, edate)
    df["mid"] = (df["고가"]+df["저가"])/2
    df = df.set_index("일자")
    df = df.rename(columns={"고가":"high","저가":"low"})

    return df

def kospi_common_stock():
    obj = db.stock.StockBasicInfo()
    df = obj.read_db(obj.columns)
    df = df.loc[(df["시장구분"]=="KOSPI") & (df["주식종류"]=="보통주")]
    df.index = range(len(df))

    return df


def stock_info(stock_name):
    obj= db.stock.StockBasicInfo()
    df = obj.read_db(obj.columns)
    scode = db.stock.name_to_code(stock_name)[1]
    df = df.loc[df["단축코드"]==scode]

    return df

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
    df = df.loc[~(df == 0).any(axis=1)] # data 0을 가진 것 제거
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



