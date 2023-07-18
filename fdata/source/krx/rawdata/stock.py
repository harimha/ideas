import pandas as pd
import requests as req
from fdata.source.base import KRX
from fdata.utils.datetimes import date_format


pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


class Stock():
    def _get_market_id(self, market_id="KOSPI"):
        if market_id == "KOSPI":
            return "STK"
        elif market_id == "KOSDAQ":
            return "KSQ"
        elif market_id == "KONEX":
            return "KNX"

    def _get_stock_code(self) -> pd.DataFrame:
        params = {"locale": "ko_KR",
                  "bld": "dbms/comm/finder/finder_stkisu",
                  "mktsel": "ALL"  # 전체
                  }
        resp = req.post("http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd", params)
        df = pd.DataFrame(resp.json()["block1"])

        return df

    def _get_full_short_code(self, stock_name):
        df = self._get_stock_code()
        code_df = df[["full_code", "short_code"]][df["codeName"] == stock_name].iloc[0]
        full_code, short_code = tuple(code_df)

        return full_code, short_code


class 주식코드검색(Stock, KRX):
    def __init__(self):
        super().__init__()
        self._params.update(bld="dbms/comm/finder/finder_stkisu",
                            mktsel="ALL")

    def get_response(self):
        params = self._set_params()
        resp = req.post(self._url, params)

        return resp

    def get_raw_data(self):
        resp = self.get_response()
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["block1"])

        return df

    def get_data(self):
        df = self.get_raw_data()
        df.drop(["ord1", "ord2"], axis=1, inplace=True)
        columns = ['full_code', 'short_code', 'stock_name', 'market_code', 'market_name', 'market_eng_name']
        df.columns = columns

        return df


class 개별종목시세추이(Stock, KRX):
    def __init__(self):
        super().__init__()
        self._params.update(bld="dbms/MDC/STAT/standard/MDCSTAT01701",
                            share="1", # 단위 : 주
                            money="1") # 단위 : 원

    def _adj_price_check(self, adj_price=False):
        if adj_price:
            return "2"
        else:
            return "1"

    def get_response(self, fcode, sdate, edate, adj_price=False):
        params = self._set_params()
        sdate, edate = date_format(sdate, edate, to_string=True)
        adj_price = self._adj_price_check(adj_price)
        params.update(isuCd=fcode,
                      strtDd=sdate,
                      endDd=edate,
                      adjStkPrc=adj_price)
        resp = req.post(self._url, params)

        return resp

    def get_raw_data(self, fcode, sdate, edate, adj_price=False):
        resp = self.get_response(fcode, sdate, edate, adj_price)
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["output"])

        return df

    def get_data(self, fcode, sdate, edate, adj_price=False):
        df = self.get_raw_data(fcode, sdate, edate, adj_price)
        df.drop(["FLUC_TP_CD", "CMPPREVDD_PRC", "FLUC_RT"], axis=1, inplace=True)
        columns = ['일자', '종가', '시가', '고가', '저가', '거래량', '거래대금', '시가총액', '상장주식수']
        df.columns = columns

        return df


class 전종목기본정보(Stock, KRX):
    def __init__(self):
        super().__init__()
        self._params.update(bld="dbms/MDC/STAT/standard/MDCSTAT01901",
                            mktId="ALL",
                            share="1") # 단위 : 주

    def get_response(self):
        params = self._set_params()
        resp = req.post(self._url, params)

        return resp

    def get_raw_data(self):
        resp = self.get_response()
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["OutBlock_1"])

        return df

    def get_data(self):
        df = self.get_raw_data()
        columns = ['표준코드', '단축코드', '한글종목명', '한글종목약명', '영문종목명',
                   '상장일', '시장구분', '증권구분', '소속부', '주식종류', '액면가',
                   '상장주식수']
        df.columns = columns

        return df


class 투자자별거래실적일별추이(Stock, KRX):
    def __init__(self):
        super().__init__()
        self._params.update(bld="dbms/MDC/STAT/standard/MDCSTAT02203",
                            inqTpCd="2", # 조회구분(1:기간합계, 2:일별추이)
                            trdVolVal="2", # 1:거래량, 2:거래대금
                            askBid="3", # 1:매도, 2:매수 3:순매수
                            segTpCd="ALL",
                            detailView="1", #상세뷰
                            money="1") # 단위 : 원

    def get_response(self, sdate, edate, market_id="KOSPI", etf=False, etn=False, elw=False):
        params = self._set_params()
        sdate, edate = date_format(sdate, edate, to_string=True)
        if market_id=="KOSPI":
            if etf :
                params.update(etf="EF")
            if etn :
                params.update(etn="EN")
            if elw :
                params.update(elw="EW")
        market_id =self._get_market_id(market_id)
        params.update(mktId=market_id,
                      strtDd=sdate,
                      endDd=edate)
        resp = req.post(self._url, params)

        return resp

    def get_raw_data(self, sdate, edate, market_id="KOSPI", etf=False, etn=False, elw=False):
        resp = self.get_response(sdate, edate, market_id, etf, etn, elw)
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["output"])

        return df

    def get_data(self, sdate, edate, market_id="KOSPI", etf=False, etn=False, elw=False):
        df = self.get_raw_data(sdate, edate, market_id, etf, etn, elw)
        df.drop("TRDVAL_TOT", axis=1, inplace=True)
        columns = ['일자', '금융투자', '보험', '투신', '사모',
                   '은행', '기타금융', '연기금등', '기타법인', '개인', '외국인',
                   '기타외국인']
        df.columns = columns

        return df


class 투자자별거래실적일별추이_개별종목(Stock, KRX):
    def __init__(self):
        super().__init__()
        self._params.update(bld="dbms/MDC/STAT/standard/MDCSTAT02303",
                            inqTpCd="2", # 조회구분(1:기간합계, 2:일별추이)
                            trdVolVal="2", # 1:거래량, 2:거래대금
                            askBid="3", # 1:매도, 2:매수 3:순매수
                            detailView="1", #상세뷰
                            money="1") # 단위 : 원

    def get_response(self, fcode, sdate, edate):
        params = self._set_params()
        sdate, edate = date_format(sdate, edate, to_string=True)
        params.update(isuCd=fcode,
                      strtDd=sdate,
                      endDd=edate)
        resp = req.post(self._url, params)

        return resp

    def get_raw_data(self, fcode, sdate, edate):
        resp = self.get_response(fcode, sdate, edate)
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["output"])

        return df

    def get_data(self, fcode, sdate, edate):
        df = self.get_raw_data(fcode, sdate, edate)
        df.drop("TRDVAL_TOT", axis=1, inplace=True)
        columns = ['일자', '금융투자', '보험', '투신', '사모',
                   '은행', '기타금융', '연기금등', '기타법인', '개인', '외국인',
                   '기타외국인']
        df.columns = columns

        return df


class 프로그램매매(Stock, KRX):
    def __init__(self):
        super().__init__()
        self._params.update(bld="dbms/MDC/STAT/standard/MDCSTAT02601",
                            share="1", # 단위 : 주
                            money="1") # 단위 : 원

    def get_response(self, sdate, edate, market_id="KOSPI"):
        params = self._set_params()
        sdate, edate = date_format(sdate, edate, to_string=True)
        market_id =self._get_market_id(market_id)
        params.update(mktId=market_id, strtDd=sdate, endDd=edate)
        resp = req.post(self._url, params)

        return resp

    def get_raw_data(self, sdate, edate, market_id="KOSPI"):
        resp = self.get_response(sdate, edate, market_id)
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["output"])

        return df

    def get_data(self, sdate, edate, market_id="KOSPI"):
        df = self.get_raw_data(sdate, edate, market_id)
        columns = ['구분', '거래량_매도', '거래량_매수', '거래량_순매수',
                   '거래대금_매도', "거래대금_매수", "거래대금_순매수"]
        df.columns = columns

        return df


class 상장회사상세검색(Stock, KRX):
    def __init__(self):
        super().__init__()
        self._params.update(bld="dbms/MDC/STAT/standard/MDCSTAT03402",
                            mktTpCd= "0", # 전체조회
                            isuSrtCd= "ALL",
                            isuSrtCd2= "ALL",
                            sortType= "A",
                            stdIndCd= "ALL",
                            sectTpCd= "ALL",
                            parval= "ALL",
                            mktcap= "ALL",
                            acntclsMm= "ALL",
                            condListShrs= "1",
                            condCap= "1",
                            share="1", # 단위 : 주
                            money="1") # 단위 : 원

    def get_response(self):
        params = self._set_params()
        resp = req.post(self._url, params)

        return resp

    def get_raw_data(self):
        resp = self.get_response()
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["block1"])

        return df

    def get_data(self):
        df = self.get_raw_data()
        columns = ['종목코드', '종목명', '시장구분', '소속부', '상장특례',
       '업종코드', '업종명', '결산월', '지정자문인', '상장주식수',
       '액면가', '자본금', '통화구분', '대표이사', '대표전화', '주소']
        df.columns = columns

        return df


class PER_PBR_배당수익률_개별종목(Stock, KRX):
    def __init__(self):
        super().__init__()
        self._params.update(bld="dbms/MDC/STAT/standard/MDCSTAT03502",
                            searchType= "2", # 개별추이
                            mktId="ALL")

    def get_response(self, fcode, sdate, edate):
        params = self._set_params()
        sdate, edate = date_format(sdate, edate, to_string=True)
        params.update(isuCd= fcode, strtDd= sdate, endDd= edate)
        resp = req.post(self._url, params)

        return resp

    def get_raw_data(self, fcode, sdate, edate):
        resp = self.get_response(fcode, sdate, edate)
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["output"])

        return df

    def get_data(self, fcode, sdate, edate):
        df = self.get_raw_data(fcode, sdate, edate)
        df.drop(['FLUC_TP_CD', 'CMPPREVDD_PRC','FLUC_RT'], axis=1, inplace=True)
        columns = ['일자', '종가', 'EPS', 'PER', 'FWD_EPS', 'FWD_PER', 'BPS', 'PBR', 'DPS', 'DVD_YLD']
        df.columns = columns

        return df


class 외국인보유량추이(Stock, KRX):
    def __init__(self):
        super().__init__()
        self._params.update(bld="dbms/MDC/STAT/standard/MDCSTAT03601",
                            segTpCd= "ALL",
                            share= "1", # 단위: 주
                            money= "1") # 단위: 원

    def get_response(self, sdate, edate, market_id="KOSPI"):
        params = self._set_params()
        sdate, edate = date_format(sdate, edate, to_string=True)
        market_id= self._get_market_id(market_id)
        params.update(mktId= market_id, strtDd= sdate, endDd= edate)
        resp = req.post(self._url, params)

        return resp

    def get_raw_data(self, sdate, edate, market_id="KOSPI"):
        resp = self.get_response(sdate, edate, market_id)
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["block1"])

        return df

    def get_data(self, sdate, edate, market_id="KOSPI"):
        df = self.get_raw_data(sdate, edate, market_id)
        columns = ['일자', '시가총액_전체', '시가총액_외국인보유', '시가총액_외국인비율', '주식수_전체',
       '주식수_외국인보유', '주식수_외국인비율']
        df.columns = columns

        return df


class 외국인보유량_개별종목(Stock, KRX):
    def __init__(self):
        super().__init__()
        self._params.update(bld="dbms/MDC/STAT/standard/MDCSTAT03702",
                            searchType= "2", #개별추이
                            mktId= "ALL",
                            share="1")  # 단위: 주

    def get_response(self, fcode, sdate, edate):
        params = self._set_params()
        sdate, edate = date_format(sdate, edate, to_string=True)
        params.update(isuCd= fcode, strtDd=sdate, endDd=edate)
        resp = req.post(self._url, params)

        return resp

    def get_raw_data(self, fcode, sdate, edate):
        resp = self.get_response(fcode, sdate, edate)
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["output"])

        return df

    def get_data(self, fcode, sdate, edate):
        df = self.get_raw_data(fcode, sdate, edate)
        df.drop(['FLUC_TP_CD', 'CMPPREVDD_PRC','FLUC_RT'], axis=1, inplace=True)
        columns = ['일자', '종가', '상장주식수', '외국인보유수량', '외국인지분율',
                   '외국인한도수량','외국인한도소진율']
        df.columns = columns

        return df


class 업종별분포(Stock, KRX):
    def __init__(self):
        super().__init__()
        self._params.update(bld="dbms/MDC/STAT/standard/MDCSTAT03801",
                            searchType= "1", #전종목
                            share="1",  # 단위: 주
                            money="1")  # 단위: 원

    def get_response(self, search_date, market_id="KOSPI"):
        params = self._set_params()
        search_date = date_format(search_date, to_string=True)
        market_id = self._get_market_id(market_id)
        params.update(mktId= market_id, trdDd= search_date)
        resp = req.post(self._url, params)

        return resp

    def get_raw_data(self, search_date, market_id="KOSPI"):
        resp = self.get_response(search_date, market_id)
        self._check_response(resp)
        df = pd.DataFrame(resp.json()["block1"])

        return df

    def get_data(self, search_date, market_id="KOSPI"):
        df = self.get_raw_data(search_date, market_id)
        columns = ['업종명', '회사수', '종목수', '상장주식수','시가총액_금액', '시가총액_비중',
                   '거래량_수량', '거래량_비중', '거래대금_금액','거래대금_비중']
        df.columns = columns

        return df

