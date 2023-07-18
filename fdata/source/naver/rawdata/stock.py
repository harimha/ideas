import requests as req
import pandas as pd
from fdata.source.base import NAVER
from fdata.utils.datetimes import date_format

class 개별종목시세추이(NAVER):
    def __init__(self):
        super().__init__()
        self._params.update(requestType="1",
                            timeframe="day")

    def get_response(self, scode, sdate, edate):
        params = self._set_params()
        sdate, edate = date_format(sdate, edate, to_string=True)
        params.update(symbol=scode,
                      startTime=sdate,
                      endTime=edate)
        resp = req.post(self._url, params)

        return resp

    def get_raw_data(self, scode, sdate, edate):
        resp = self.get_response(scode, sdate, edate)
        self._check_response(resp)
        resp = resp.text.strip()
        data_list = eval(resp)
        df = pd.DataFrame(data_list[1:], columns=data_list[0])

        return df

    def get_data(self, scode, sdate, edate):
        df = self.get_raw_data(scode, sdate, edate)
        df.drop("외국인소진율", axis=1, inplace=True)
        df.columns = ["일자", "시가", "고가", "저가", "종가", "거래량"]

        return df

