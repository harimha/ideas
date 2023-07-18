import calendar
import requests as req
from bs4 import BeautifulSoup
from datetime import datetime
from fdata.utils.types import is_datetime_like, is_timestamp



def get_last_day_of_month(year, month):
    if isinstance(year, str):
        year = int(year)
    if isinstance(month, str):
        month = int(month)

    last_day = calendar.monthrange(year, month)[1]

    return last_day


def date_format(*date, to_string=False) -> datetime or str:
    '''
    파라미터로 넘기는 date format 일치시키는 기능
    20230601, 2023-06-01, datetime 객체 모두 사용 가능
    return : %Y%m%d 형태의 datetime , YYYYmmdd 형태의 str객체 반환
    '''
    d_lst = []
    for d in date:
        if to_string :
            if is_datetime_like(d):
                d = d.strftime("%Y%m%d")
            elif d.find("-") > 0:
                d = d.replace("-","")
        else:
            if is_timestamp(d):
                d = d.to_pydatetime()
            elif is_datetime_like(d):
                pass
            elif d.find("-") > 0:
                d = d.replace("-", "")
                d = datetime.strptime(d,"%Y%m%d")
            else:
                d = datetime.strptime(d,"%Y%m%d")
        d_lst.append(d)

    return d_lst

def get_last_buisiness_day():
    resp = req.get("https://finance.naver.com/sise/sise_index.naver?code=KOSPI")
    bs = BeautifulSoup(resp.text, "lxml")
    date_str = bs.select(".date")[0].text.split(" ")[0]
    last_buisiness_day = datetime.strptime(date_str, "%Y-%m-%d")

    return last_buisiness_day

