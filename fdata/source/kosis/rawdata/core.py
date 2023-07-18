import requests as req
import pandas as pd
from fdata.source.base import KOSIS


class 통계목록(KOSIS):
    def __init__(self):
        super().__init__()
        self._url = "https://kosis.kr/openapi/statisticsList.do"
        self._params.update(method="getList")
        self._params.update(vwCd="MT_ZTITLE") # 국내통계 주제별

    def get_response(self):
        params = self._set_params()
        params.update(parentListId="S1") # 금융
        resp = req.get(self._url, params)

        return resp

    def get_raw_data(self):
        resp = self.get_response()
        df = pd.DataFrame(resp.json())

        return df

    def get_data(self):
        df = self.get_raw_data()
        return df



class 통계자료(API):

    def __init__(self, apiKey):
        super().__init__(apiKey)
        self.params.update(method="getList")

    @property
    def url(self):
        return "https://kosis.kr/openapi/Param/statisticsParameterData.do"


    def get_data(self, orgId, tblId, objL1, itmId, prdSe, startPrdDe, endPrdDe) -> DataFrame:
        '''
        :param orgId: 기관 ID
        :param tblId: 통계표 ID
        :param objL1: 분류1(첫번째 분류코드)
        :param itmId: 항목
        :param prdSe: 수록주기
        :param startPrdDe: 시작수록시점
        :param endPrdDe: 종료수록시점
        :return:
        ORG_ID: 기관코드
        TBL_ID: 통계표ID
        TBL_NM: 통계표명
        C1 ~ C8: 분류값 ID1 ~ 분류값 ID8	2~8 분류값은
        없을 경우 생략
        C1_OBJ_NM ~ C8_OBJ_NM: 분류명1 ~ 분류명8
        C1_OBJ_NM_ENG ~ C8_OBJ_NM_ENG: 분류 영문명1 ~ 분류 영문명8
        C1_NM ~ C8_NM: 분류값 명1 ~ 분류값 명8
        C1_NM_ENG ~ C8_NM_ENG: 분류값 영문명1 ~ 분류값 영문명8
        ITM_ID: 항목 ID
        ITM_NM: 항목명
        ITM_NM_ENG: 항목영문명
        UNIT_ID: 단위ID
        UNIT_NM: 단위명
        UNIT_NM_ENG: 단위영문명
        PRD_SE: 수록주기	수록주기
        PRD_DE: 수록시점
        DT: 수치값
        '''
        df= super()._get_data(orgId=orgId, tblId=tblId, objL1=objL1,
                              itmId=itmId, prdSe=prdSe, startPrdDe=startPrdDe,
                              endPrdDe=endPrdDe)
        return df


class 통화금융통계(통계자료):

    def __init__(self, apiKey):
        super().__init__(apiKey)
        self.orgId = "301"


    def M2상품별구성내역(self, prdSe, startPrdDe, endPrdDe, EOP, SA) -> DataFrame:

        if EOP:
            if SA:
                # 말잔, 계절조정
                df = self.get_data(orgId=self.orgId,
                                   tblId="DT_101Y001",
                                   objL1="13102134693ACC_ITEM.BBGS00",
                                   itmId="13103134693999",
                                   prdSe=prdSe,
                                   startPrdDe=startPrdDe,
                                   endPrdDe=endPrdDe)
                return df

            else :
                # 말잔, 원계열
                df = self.get_data(orgId=self.orgId,
                                   tblId="DT_101Y002",
                                   objL1="13102134509ACC_ITEM.BBGA00",
                                   itmId="13103134509999",
                                   prdSe=prdSe,
                                   startPrdDe=startPrdDe,
                                   endPrdDe=endPrdDe)

                return df

        else:
            if SA:
                # 평잔, 계절조정
                df = self.get_data(orgId=self.orgId,
                                   tblId="DT_101Y003",
                                   objL1="13102134507ACC_ITEM.BBHS00",
                                   itmId="13103134507999",
                                   prdSe=prdSe,
                                   startPrdDe=startPrdDe,
                                   endPrdDe=endPrdDe)
                return df

            else :
                # 평잔, 원계열
                df = self.get_data(orgId=self.orgId,
                                   tblId="DT_101Y004",
                                   objL1="13102134508ACC_ITEM.BBHA00",
                                   itmId="13103134508999",
                                   prdSe=prdSe,
                                   startPrdDe=startPrdDe,
                                   endPrdDe=endPrdDe)
                return df