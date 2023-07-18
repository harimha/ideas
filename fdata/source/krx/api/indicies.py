import pandas as pd
from fdata.utils import dfhandling
from fdata.db.mysql.utils.utils import read_db
from fdata.source.krx.rawdata.indicies \
    import 개별지수시세추이, 주가지수코드검색, 전체지수기본정보, 지수구성종목, PER_PBR_배당수익률


def get_index_code() -> pd.DataFrame:
    '''지수 코드 관련 데이터'''
    obj = 주가지수코드검색()
    df = obj.get_data()

    return df

def get_fcode_scode(index_name):
    try:
        df = read_db("indicies", "index_code",("full_code", "short_code", "index_name"))
        df = df[["full_code", "short_code"]][df["index_name"]==index_name]
        fcode, scode = tuple(df.iloc[0])

    except:
        df = get_index_code()
        df = df[["full_code", "short_code"]][df["index_name"]==index_name]
        fcode, scode = tuple(df.iloc[0])

    return fcode, scode

def get_index_ohlcv(index_name, sdate, edate) -> pd.DataFrame:
    '''
    :param index_name: ex)코스피200
    :param sdate: 조회시작일
    :param edate: 조회 종료일
    '''
    obj = 개별지수시세추이()
    fcode, scode = get_fcode_scode(index_name)
    df = obj.get_data(fcode, scode, sdate, edate)
    df.drop(["대비","등락률"], axis=1, inplace=True)
    col_datetime = df.columns[:1]
    col_float = df.columns[1:5]
    col_int = df.columns[5:]
    df = dfhandling.remove_hyphen(df, zero=True)
    df = dfhandling.remove_comma(df,df.columns)
    df = dfhandling.change_type(df,
                                datetime=col_datetime,
                                float=col_float,
                                int=col_int)
    df["index_name"] = index_name

    return df

def get_index_info():
    obj = 전체지수기본정보()
    index_class_list = ["KRX", "KOSPI", "KOSDAQ", "테마"]
    df = pd.DataFrame(columns=["지수명", "영문지수명", "기준일", "발표일", "기준지수",
                               "산출주기", "산출시간", "구성종목수", "full_code",
                               "short_code","index_class"])
    for index_class in index_class_list:
        df_data = obj.get_data(index_class)
        df_data["index_class"] = index_class
        df = pd.concat([df,df_data],axis=0)
    col_datetime = ["기준일", "발표일"]
    col_float = ["기준지수"]
    col_int = ["구성종목수"]
    df = dfhandling.remove_comma(df, df.columns)
    df = dfhandling.change_type(df,
                                datetime=col_datetime,
                                float=col_float,
                                int=col_int)
    df.drop(["full_code", "short_code"], axis=1, inplace=True)
    df.index = range(len(df))

    return df

def get_index_components(index_name, search_date):
    obj = 지수구성종목()
    scode, fcode = get_fcode_scode(index_name)
    df = obj.get_data(scode, fcode, search_date)
    df = df[["종목코드", "종목명", "종가", "상장시가총액"]]
    int_col = ["종가", "상장시가총액"]
    df = dfhandling.remove_comma(df, df.columns)
    df = dfhandling.change_type(df, int=int_col)
    df["조회일"] = search_date
    df["지수명"] = index_name

    return df

def get_index_per_pbr_div(index_name, sdate, edate):
    obj = PER_PBR_배당수익률()
    scode, fcode = get_fcode_scode(index_name)
    df = obj.get_data(scode, fcode, sdate, edate)
    df["지수명"] = index_name
    df.drop(["종가", "선행PER", "대비", "등락률"], axis=1, inplace=True)
    col_datetime = ["일자"]
    col_float = ["PER", "PBR", "배당수익률"]
    df = dfhandling.remove_hyphen(df)
    df = dfhandling.remove_comma(df, df.columns)
    df = dfhandling.change_type(df, datetime=col_datetime, float=col_float)

    return df

