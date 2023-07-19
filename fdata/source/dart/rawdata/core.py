from fdata.source.base import DART
import pandas as pd
import requests as req
from os.path import isdir, dirname, isfile
from zipfile import ZipFile
from io import BytesIO
from xml.etree.ElementTree import parse
from fdata.db.mysql.finance.wrap import get_ccode_from_db
from fdata.db.mysql.stock.utils import name_to_code, scode_to_name


pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


class 고유번호(DART):
    def __init__(self):
        super().__init__()
        self._url = "https://opendart.fss.or.kr/api/corpCode.xml"

    @get_ccode_from_db
    def _get_corp_code(self, stock_name):
        df = self.get_data()
        scode = name_to_code(stock_name)[1]
        corp_code = df["corp_code"][df["stock_code"]==scode].iloc[0]
        print("test")
        return corp_code

    def _save_corp_code(self):
        dir_path = "fdata/source/dart/corp_code"
        if isdir(dir_path):
            pass
        else:
            os.mkdir(dir_path)
        resp = self.get_response()
        with ZipFile(BytesIO(resp.content)) as zipfile:
            zipfile.extractall(dir_path)

    def get_response(self):
        resp = req.get(self._url, self._params)

        return resp

    def get_raw_data(self):
        file_path = "fdata/source/dart/corp_code/CORPCODE.xml"
        if isfile(file_path):
            pass
        else:
            self._save_corp_code()
        xmlTree = parse(file_path)
        root = xmlTree.getroot()
        lst = root.findall('list')
        corp_code = [lst[i].findtext("corp_code") for i in range(len(lst))]
        corp_name = [lst[i].findtext("corp_name") for i in range(len(lst))]
        stock_code = [lst[i].findtext("stock_code") for i in range(len(lst))]
        modify_date = [lst[i].findtext("modify_date") for i in range(len(lst))]

        df = pd.DataFrame(data={"corp_code": corp_code,
                                "corp_name": corp_name,
                                "stock_code": stock_code,
                                "modify_date": modify_date})

        return df

    def get_data(self):
        df = self.get_raw_data()
        df["stock_code"] = df["stock_code"].replace(" ", None)
        df = df.dropna()
        df.index = range(len(df))

        return df


class 단일회사주요계정(DART):
    def __init__(self):
        super().__init__()
        self._url = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json"

    def _get_report_code(self, quarter):
        '''
        1분기보고서 : 11013
        반기보고서 : 11012
        3분기보고서 : 11014
        사업보고서 : 11011
        '''
        if quarter == "1Q":
            return "11013"
        elif quarter == "2Q":
            return "11012"
        elif quarter == "3Q":
            return "11014"
        else:
            return "11011"

    def _get_fs_div(self, fs_name="연결"):
        '''개별재무제표/연결재무제표 구분 코드 반환'''
        if fs_name == "연결":
            return "CFS"
        else:
            return "OFS"

    def get_response(self, corp_code, year, quarter="4Q"):
        params = self._set_params()
        report_code = self._get_report_code(quarter)
        params.update(corp_code=corp_code,
                      bsns_year=year,
                      reprt_code=report_code)
        resp = req.get(self._url, params)

        return resp

    def get_raw_data(self, corp_code, year, quarter="4Q"):
        resp = self.get_response(corp_code, year, quarter)
        df = pd.DataFrame(resp.json()["list"])

        return df


class 다중회사주요계정(DART):
    pass

class 재무제표원본(DART):
    pass

class 단일회사전체재무제표(DART):
    pass