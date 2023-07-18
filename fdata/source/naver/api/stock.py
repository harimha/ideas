from fdata.utils import dfhandling
from fdata.utils.exceptions import DBNotFoundError
from fdata.db.mysql.utils.utils import read_db
from fdata.source.naver.rawdata.stock import 개별종목시세추이


def get_fcode_scode(stock_name):
    try:
        df = read_db("stock", "stock_code", ("full_code", "short_code", "stock_name"))
        df = df[["full_code", "short_code"]][df["stock_name"]==stock_name]
        fcode, scode = tuple(df.iloc[0])
    except:
        raise DBNotFoundError

    return fcode, scode


def get_stock_ohlcv(stock_name, sdate, edate):
    obj = 개별종목시세추이()
    scode = get_fcode_scode(stock_name)[1]
    df = obj.get_data(scode, sdate, edate)
    col_datetime = ["일자"]
    df = dfhandling.change_type(df, datetime=col_datetime)
    df["stock_name"] = stock_name

    return df




