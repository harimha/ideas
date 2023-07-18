from fdata.utils import dfhandling
from fdata.db.mysql.utils.utils import read_db
from fdata.source.krx.rawdata.stock \
    import 주식코드검색, 개별종목시세추이, 전종목기본정보, 투자자별거래실적일별추이,\
    투자자별거래실적일별추이_개별종목, 상장회사상세검색, PER_PBR_배당수익률_개별종목,\
    외국인보유량추이, 외국인보유량_개별종목, 업종별분포


def get_stock_code():
    obj = 주식코드검색()
    df = obj.get_data()

    return df

def get_fcode_scode(stock_name):
    try:
        df = read_db("stock", "stock_code", ("full_code", "short_code", "stock_name"))
        df = df[["full_code", "short_code"]][df["stock_name"]==stock_name]
        fcode, scode = tuple(df.iloc[0])
    except:
        df = get_stock_code()
        df = df[["full_code", "short_code"]][df["stock_name"]==stock_name]
        fcode, scode = tuple(df.iloc[0])

    return fcode, scode

def get_basic_info():
    obj = 전종목기본정보()
    df = obj.get_data()
    df = dfhandling.remove_hyphen(df, zero=False)
    df = dfhandling.remove_comma(df, df.columns)
    df["액면가"][df["액면가"]=="무액면"] = None
    col_datetime = ["상장일"]
    col_float = ["액면가"]
    col_int = ['상장주식수']
    df = dfhandling.change_type(df,
                                datetime=col_datetime,
                                float=col_float,
                                int=col_int)
    return df

def get_stock_ohlcv(stock_name, sdate, edate, adj_price):
    '''
    거래소에서 전기간 조회를 막아두면서 adj_price가 일관성이 없어짐
    '''
    obj = 개별종목시세추이()
    fcode = get_fcode_scode(stock_name)[0]
    df = obj.get_data(fcode, sdate, edate, adj_price)
    df = dfhandling.remove_hyphen(df, zero=True)
    df = dfhandling.remove_comma(df, df.columns)
    col_datetime = ["일자"]
    col_int = ['종가', '시가', '고가', '저가', '거래량', '거래대금', '시가총액', '상장주식수']
    df = dfhandling.change_type(df,
                                datetime=col_datetime,
                                int=col_int)
    df["stock_name"] = stock_name

    return df

def get_investor_trading_trend_market(sdate, edate, market_id="KOSPI", etf=False, etn=False, elw=False):
    obj = 투자자별거래실적일별추이()
    df = obj.get_data(sdate, edate, market_id, etf, etn, elw)
    df = dfhandling.remove_hyphen(df, zero=True)
    df = dfhandling.remove_comma(df, df.columns)
    col_datetime = ["일자"]
    col_int = ['금융투자', '보험', '투신', '사모', '은행', '기타금융', '연기금등', '기타법인', '개인',
       '외국인', '기타외국인']
    df = dfhandling.change_type(df,
                                datetime=col_datetime,
                                int=col_int)
    df["market"] = market_id

    return df

def get_investor_trading_trend_stock(stock_name, sdate, edate):
    obj = 투자자별거래실적일별추이_개별종목()
    fcode = get_fcode_scode(stock_name)[0]
    df = obj.get_data(fcode, sdate, edate)
    df = dfhandling.remove_hyphen(df, zero=True)
    df = dfhandling.remove_comma(df, df.columns)
    col_datetime = ["일자"]
    col_int = ['금융투자', '보험', '투신', '사모', '은행', '기타금융', '연기금등', '기타법인', '개인',
               '외국인', '기타외국인']
    df = dfhandling.change_type(df,
                                datetime=col_datetime,
                                int=col_int)
    df["stock_name"] = stock_name

    return df

def get_listed_company_details():
    obj = 상장회사상세검색()
    df = obj.get_data()
    df = dfhandling.remove_hyphen(df, zero=False)
    df = dfhandling.remove_comma(df, df.columns)
    df["액면가"][df["액면가"]=="무액면"] = None
    col_float = ["액면가"]
    col_int = ['상장주식수', '자본금']
    df = dfhandling.change_type(df,
                                int=col_int,
                                float=col_float)

    return df

def get_stock_PER_PBR_Div(stock_name, sdate, edate):
    obj = PER_PBR_배당수익률_개별종목()
    fcode = get_fcode_scode(stock_name)[0]
    df = obj.get_data(fcode, sdate, edate)
    df = dfhandling.remove_hyphen(df, zero=False)
    df = dfhandling.remove_comma(df, df.columns)
    col_datetime = ["일자"]
    col_int = ['종가', 'EPS', 'BPS', 'DPS']
    col_float = ['PER', 'PBR', 'DVD_YLD']
    df = dfhandling.change_type(df,
                                datetime=col_datetime,
                                float=col_float,
                                int=col_int)
    df["stock_name"] = stock_name

    return df

def get_foreign_holdings_market(sdate, edate, market_id="KOSPI"):
    obj = 외국인보유량추이()
    df = obj.get_data(sdate, edate, market_id)
    df = dfhandling.remove_hyphen(df, zero=False)
    df = dfhandling.remove_comma(df, df.columns)
    col_datetime = ["일자"]
    col_int = ['시가총액_전체', '시가총액_외국인보유', '주식수_전체', '주식수_외국인보유']
    col_float = ['시가총액_외국인비율', '주식수_외국인비율']
    df = dfhandling.change_type(df,
                                datetime=col_datetime,
                                float=col_float,
                                int=col_int)
    df["market"] = market_id

    return df

def get_foreign_holdings_stock(stock_name, sdate, edate):
    obj = 외국인보유량_개별종목()
    fcode = get_fcode_scode(stock_name)[0]
    df = obj.get_data(fcode, sdate, edate)
    df = dfhandling.remove_hyphen(df, zero=False)
    df = dfhandling.remove_comma(df, df.columns)
    col_datetime = ["일자"]
    col_int = ['종가', '상장주식수', '외국인보유수량', '외국인한도수량']
    col_float = ['외국인지분율', '외국인한도소진율']
    df = dfhandling.change_type(df,
                                datetime=col_datetime,
                                float=col_float,
                                int=col_int)
    df["stock_name"] = stock_name

    return df

def get_industry_distribution(search_date, market_id="KOSPI"):
    obj = 업종별분포()
    df = obj.get_data(search_date, market_id)
    df = dfhandling.remove_hyphen(df, zero=False)
    df = dfhandling.remove_comma(df, df.columns)
    col_int = ['회사수', '종목수', '상장주식수', '시가총액_금액', '거래량_수량', '거래대금_금액']
    col_float = ['시가총액_비중', '거래량_비중', '거래대금_비중']
    df = dfhandling.change_type(df,
                                float=col_float,
                                int=col_int)

    return df

