import pandas as pd
from pandas.api.types import is_list_like


def remove_hyphen(df, zero=False):
    if zero :
        df = df.replace("-","0")
    else:
        df = df.replace("-",None)

    return df

def remove_comma(df, columns):
    '''
    해당 열의 자리 구분 ","을 제거하는 기능
    :param columns: "str" or "list_like"
    '''
    if is_list_like(columns):
        for col in columns:
            df[col] = df[col].str.replace(",", "")
    else:
        df[columns] = df[columns].str.replace(",", "")

    return df

def change_type(df, **kwargs):
    '''
    데이터 타입 변경
    :param kwargs: 타입명="칼럼명" or 타입명=list_like
    ex) datetime="일자",float=["종가", "대비", "등락률", "시가", "고가", "저가"],int=columns[:4]
    :return:
    '''
    types = kwargs.keys()
    for target_type in types:
        col_name = kwargs[target_type]
        if target_type == "datetime":
            if is_list_like(col_name):
                for col in col_name:
                    df[col] = pd.to_datetime(df[col])
            else :
                df[col_name] = pd.to_datetime(df[col_name])
        elif target_type == "int":
            target_type = "int64"
            if is_list_like(col_name):
                for col in col_name:
                    df[col] = df[col].astype(target_type)
            else :
                df[col_name] = df[col_name].astype(target_type)
        else:
            if is_list_like(col_name):
                for col in col_name:
                    df[col] = df[col].astype(target_type)
            else :
                df[col_name] = df[col_name].astype(target_type)

    return df
