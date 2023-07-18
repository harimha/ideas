import requests as req
import pandas as pd
from fdata.source.base import ECOS
from fdata.utils.datetimes import get_last_day_of_month

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


class 통계목록(ECOS):
    def __init__(self):
        super().__init__()
        self._service_name = "StatisticTableList"
        self._params = [self._url,
                        self._service_name,
                        self._apikey,
                        self._format,
                        self._lang,
                        self._spage,
                        self._epage]

    def _get_response(self, stat_code):
        params = self._set_params(stat_code)
        url = "/".join(params)
        resp = req.get(url)

        return resp

    def _get_raw_data(self, stat_code):
        resp = self._get_response(stat_code)
        resp = resp.json()[self._service_name]["row"]
        df = pd.DataFrame(resp)

        return df

    def _get_data(self, stat_code):
        df = self._get_raw_data(stat_code)
        df.columns = ["상위통계표코드", "통계표코드", "통계명", "주기", "검색가능여부", "출처"]

        return df


class 통계세부항목(ECOS):
    def __init__(self):
        super().__init__()
        self._service_name = "StatisticItemList"
        self._params = [self._url,
                        self._service_name,
                        self._apikey,
                        self._format,
                        self._lang,
                        self._spage,
                        self._epage]

    def _get_response(self, stat_code):
        params = self._set_params(stat_code)
        url = "/".join(params)
        resp = req.get(url)

        return resp

    def _get_raw_data(self, stat_code):
        resp = self._get_response(stat_code)
        resp = resp.json()[self._service_name]["row"]
        df = pd.DataFrame(resp)

        return df

    def _get_data(self, stat_code):
        df = self._get_raw_data(stat_code)
        df.columns = ["통계표코드", "통계명", "항목그룹코드", "항목그룹명", "통계항목코드",
                      "통계항목명", "상위통계항목코드", "상위통계항목명", "주기", "수록시작일자",
                      "수록종료일자", "자료수", "단위", "가중치"]

        return df


class 통계표조회(ECOS):
    def __init__(self):
        super().__init__()
        self._service_name = "StatisticSearch"
        self._params = [self._url,
                        self._service_name,
                        self._apikey,
                        self._format,
                        self._lang,
                        self._spage,
                        self._epage]

    def _convert_month_to_date(self, df):
        df["시점"] = df["시점"] + str(get_last_day_of_month(df["시점"][:4], df["시점"][4:]))
        return df

    def _convert_currency_unit(self, series):
        if series["단위"].strip() in ["십억", "십억원"]:
            series["값"] *= 1000000000
        elif series["단위"].strip() in ["억", "억원"]:
            series["값"] *= 100000000
        elif series["단위"].strip() in ["백만", "백만원"]:
            series["값"] *= 1000000
        elif series["단위"].strip() in ["천", "천원"]:
            series["값"] *= 1000

        return series

    def _get_period_type(self, type):
        if type in ["년", "연"]:
            return "A"
        elif type == "반년":
            return "S"
        elif type == "분기":
            return "Q"
        elif type == "월":
            return "M"
        elif type == "반월":
            return "SM"
        elif type == "일":
            return "D"
        else:
            return None

    def _get_response(self, stat_code, period_type, sdate, edate, *itemcode):
        period_type = self._get_period_type(period_type)
        params = self._set_params([stat_code, period_type, sdate, edate, *itemcode])
        url = "/".join(params)
        resp = req.get(url)

        return resp

    def _get_raw_data(self, stat_code, period_type, sdate, edate, *itemcode):
        resp = self._get_response(stat_code, period_type, sdate, edate, *itemcode)
        resp = resp.json()[self._service_name]["row"]
        df = pd.DataFrame(resp)

        return df

    def _get_data(self, stat_code, period_type, sdate, edate, *itemcode):
        df = self._get_raw_data(stat_code, period_type, sdate, edate, *itemcode)
        df.columns = ["통계표코드", "통계명", "통계항목코드1", "통계항목명1", "통계항목코드2",
                      "통계항목명2", "통계항목코드3", "통계항목명3", "통계항목코드4", "통계항목명4",
                      "단위", "시점", "값"]

        return df


class 통계메타(ECOS):
    def __init__(self):
        super().__init__()
        self._service_name = "StatisticMeta"
        self._params = [self._url,
                        self._service_name,
                        self._apikey,
                        self._format,
                        self._lang,
                        self._spage,
                        self._epage]

    def _get_response(self, data_name):
        params = self._set_params(data_name)
        url = "/".join(params)
        resp = req.get(url)

        return resp

    def _get_raw_data(self, data_name):
        resp = self._get_response(data_name)
        resp = resp.json()[self._service_name]["row"]
        df = pd.DataFrame(resp)

        return df

    def _get_data(self, data_name):
        df = self._get_raw_data(data_name)
        df.columns = ["레벨", "상위통계항목코드", "통계항목코드", "통계항목명", "메타데이터"]

        return df

