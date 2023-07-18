import pandas as pd
import requests as req
from fdata.source.base import KRX
from fdata.utils.datetimes import date_format


pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


class Indicies():
    def _get_index_code(self) -> pd.DataFrame:
        params = {"bld": "dbms/comm/finder/finder_equidx",
                  "mktsel": "1"  # 전체
                  }
        resp = req.post(self._url, params)
        df = pd.DataFrame(resp.json()["block1"])

        return df

    def _get_full_short_code(self, index_name):
        df = self._get_index_code()
        df["codeName"] = df["codeName"].str.replace(" ", "")
        code_df = df[["full_code", "short_code"]][df["codeName"] == index_name].iloc[0]
        full_code, short_code = tuple(code_df)

        return full_code, short_code



class 주가지수코드검색(Indicies, KRX):
    def __init__(self):
        super().__init__()
        self._params.update(bld="dbms/comm/finder/finder_equidx",
                            mktsel="1") # 전체

    def get_response(self):
        params = self._set_params()
        resp = req.post(self._url, params)

        return resp

    def get_raw_data(self) -> pd.DataFrame:
        resp = self.get_response()
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["block1"])

        return df

    def get_data(self) -> pd.DataFrame:
        df = self.get_raw_data()
        columns = ['full_code', 'short_code', 'index_name', 'market_code', 'market_name']
        df.columns = columns
        df["index_name"] = df["index_name"].str.replace(" ","")

        return df


class 개별지수시세추이(Indicies, KRX):
    def __init__(self):
        super().__init__()
        self._params.update(bld="dbms/MDC/STAT/standard/MDCSTAT00301",
                            share= "1", # 주식수단위(1:주)
                            money= "1" # 금액단위(1:원)
                            )

    def get_response(self, full_code, short_code, sdate, edate):
        params = self._set_params()
        sdate, edate = date_format(sdate, edate, to_string=True)
        params.update(indIdx=full_code, indIdx2=short_code, strtDd=sdate, endDd=edate)
        resp = req.post(url=self._url, params=params)

        return resp


    def get_raw_data(self, full_code, short_code, sdate, edate):
        resp = self.get_response(full_code, short_code, sdate, edate)
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["output"])

        return df

    def get_data(self, full_code, short_code, sdate, edate) -> pd.DataFrame:
        '''
        :param index_name_kor: ex)코스피200
        :param sdate: 시작 날짜
        :param edate: 끝 날짜
        '''
        df = self.get_raw_data(full_code, short_code, sdate, edate)
        self._check_empty_dataframe(df)
        df.drop("FLUC_TP_CD", axis=1, inplace=True)
        columns = ["일자", "종가", "대비", "등락률", "시가", "고가", "저가", "거래량", "거래대금", "상장시가총액"]
        df.columns = columns

        return df


class 전체지수기본정보(Indicies, KRX):
    def __init__(self):
        super().__init__()
        self._params.update(bld="dbms/MDC/STAT/standard/MDCSTAT00401")
        self.index_class = {"KRX": "01",
                            "KOSPI": "02",
                            "KOSDAQ": "03",
                            "테마": "04"}

    def get_response(self, index_class="KOSPI"):
        params = self._set_params()
        params.update(idxIndMidclssCd=self.index_class[index_class])
        resp = req.post(url=self._url, params=params)

        return resp

    def get_raw_data(self, index_class="KOSPI"):
        resp = self.get_response(index_class)
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["output"])

        return df

    def get_data(self, index_class="KOSPI") -> pd.DataFrame:
        df = self.get_raw_data(index_class)
        self._check_empty_dataframe(df)
        columns = ["지수명","영문지수명","기준일","발표일","기준지수","산출주기","산출시간","구성종목수","full_code","short_code"]
        df.columns = columns
        df["지수명"] = df["지수명"].str.replace(" ","")
        df["영문지수명"] = df["영문지수명"].str.replace(" ","")

        return df


class 지수구성종목(Indicies, KRX):
    def __init__(self):
        super().__init__()
        self._params.update(bld="dbms/MDC/STAT/standard/MDCSTAT00601",
                            money="1" # 원 단위
                            )

    def get_response(self, full_code, short_code, search_date):
        params = self._set_params()
        search_date = date_format(search_date, to_string=True)
        params.update(indIdx=full_code,
                      indIdx2=short_code,
                      trdDd=search_date)
        resp = req.post(url=self._url, params=params)

        return resp

    def get_raw_data(self, full_code, short_code, search_date):
        resp = self.get_response(full_code, short_code, search_date)
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["output"])

        return df

    def get_data(self, full_code, short_code, search_date) -> pd.DataFrame:
        '''
        :param index_name_kor: ex)코스피200
        :param search_date: 조회일자
        '''
        df = self.get_raw_data(full_code, short_code, search_date)
        self._check_empty_dataframe(df)
        df.drop("FLUC_TP_CD", axis=1, inplace=True)
        columns = ["종목코드","종목명","종가","대비","등락률","상장시가총액"]
        df.columns = columns

        return df


class PER_PBR_배당수익률(Indicies, KRX):
    def __init__(self):
        super().__init__()

    def get_response(self, full_code, short_code, sdate, edate):
        params = self._set_params()
        sdate, edate = date_format(sdate, edate, to_string=True)
        params.update(bld="dbms/MDC/STAT/standard/MDCSTAT00702",
                      searchType="P",  # 개별조회
                      indTpCd=full_code,
                      indTpCd2=short_code,
                      strtDd=sdate,
                      endDd=edate)
        resp = req.post(url=self._url, params=params)

        return resp

    def get_raw_data(self, full_code, short_code, sdate, edate):
        resp = self.get_response(full_code, short_code, sdate, edate)
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["output"])

        return df

    def get_data(self, full_code, short_code, sdate, edate):
        df = self.get_raw_data(full_code, short_code, sdate, edate)
        self._check_empty_dataframe(df)
        df.drop("FLUC_TP_CD", axis=1, inplace=True)
        columns = ["일자", "종가", "대비", "등락률", "PER", "선행PER", "PBR", "배당수익률"]
        df.columns = columns

        return df
