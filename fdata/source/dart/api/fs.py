import pandas as pd
from fdata.source.dart.rawdata.sub import 단일회사주요계정_1분기, 단일회사주요계정_반기, \
    단일회사주요계정_3분기, 단일회사주요계정_사업
from fdata.source.dart.rawdata.core import 고유번호
from fdata.utils import dfhandling


def get_fs(stock_name, year, quarter="4Q", fs_div="연결"):
    corp_code = 고유번호()._get_corp_code(stock_name)
    if quarter == "1Q":
        obj = 단일회사주요계정_1분기()
    elif quarter == "2Q":
        obj = 단일회사주요계정_반기()
    elif quarter == "3Q":
        obj = 단일회사주요계정_3분기()
    else:
        obj = 단일회사주요계정_사업()

    df = obj.get_data(corp_code, year)
    fs_div_code = obj._get_fs_div(fs_div)
    df = df[df["개별/연결구분"]==fs_div_code]
    df.drop("개별/연결구분", axis=1, inplace=True)
    df["접수일자"] = df["접수번호"].str[:8]
    df = dfhandling.remove_comma(df, df.columns)
    df = df[['사업연도', '접수일자', '주식코드', '재무제표구분', '계정명', '당기일자', '당기금액', '통화단위']]

    return df

def get_fs_bs(stock_name, year, quarter="4Q", fs_div="연결"):
    df = get_fs(stock_name, year, quarter, fs_div)
    df = df[df["재무제표구분"]=="BS"]
    df.drop("재무제표구분", axis=1, inplace=True)
    df["당기일자"] = df["당기일자"].str[0:-3]
    date_col = ["접수일자", "당기일자"]
    int_col = ["당기금액"]
    df = dfhandling.change_type(df,datetime=date_col,
                                int=int_col)

    return df

def get_fs_is(stock_name, year, quarter="4Q", fs_div="연결"):
    df = get_fs(stock_name, year, quarter, fs_div)
    df = df[df["재무제표구분"] == "IS"]
    df.index = range(len(df.index))
    df_tmp = pd.DataFrame(list(df["당기일자"].str.split(" ~ ")), columns=["시작일", "종료일"])
    df = pd.concat([df, df_tmp], axis=1)
    df.drop(["재무제표구분", "당기일자"], axis=1, inplace=True)
    date_col = ["접수일자", "시작일", "종료일"]
    int_col = ["당기금액"]
    df = dfhandling.change_type(df, datetime=date_col,
                                int=int_col)

    return df


