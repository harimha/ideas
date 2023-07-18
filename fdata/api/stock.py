from fdata.db.mysql.stock.tables import *


def stock_c(stock_name, sdate=None, edate=None):
    obj = StockOHLCV_NAVER()
    df= obj.read_db(stock_name, ["일자", "종가"], sdate, edate)
    df.columns = ["일자", stock_name]

    return df

def stock_v(stock_name, sdate=None, edate=None):
    obj = StockOHLCV_NAVER()
    df= obj.read_db(stock_name, ["일자", "거래량"], sdate, edate)
    df.columns = ["일자", stock_name]

    return df



