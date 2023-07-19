from fdata.source.dart.rawdata.core import 단일회사주요계정


class 단일회사주요계정_1분기(단일회사주요계정):
    def __init__(self):
        super().__init__()

    def get_data(self, corp_code, year):
        df = super().get_raw_data(corp_code, year, "1Q")
        df.drop(["reprt_code", "corp_code", "fs_nm", 'sj_nm', 'thstrm_nm',
                 'frmtrm_nm','ord'],
                axis=1, inplace=True)
        df.columns = ['접수번호', '사업연도', '주식코드', '개별/연결구분', '재무제표구분',
                      '계정명', '당기일자', '당기금액', '전기일자', '전기금액',
                      '통화단위', "당기누적금액", "전기누적금액"]
        return df


class 단일회사주요계정_반기(단일회사주요계정):
    def __init__(self):
        super().__init__()

    def get_data(self, corp_code, year):
        df = super().get_raw_data(corp_code, year, "2Q")
        df.drop(["reprt_code", "corp_code", "fs_nm", 'sj_nm', 'thstrm_nm',
                 'frmtrm_nm', 'ord'],
                axis=1, inplace=True)
        df.columns = ['접수번호', '사업연도', '주식코드', '개별/연결구분', '재무제표구분',
                      '계정명', '당기일자', '당기금액', '전기일자', '전기금액',
                      '통화단위', "당기누적금액", "전기누적금액"]
        return df


class 단일회사주요계정_3분기(단일회사주요계정):
    def __init__(self):
        super().__init__()

    def get_data(self, corp_code, year):
        df = super().get_raw_data(corp_code, year, "3Q")
        df.drop(["reprt_code", "corp_code", "fs_nm", 'sj_nm', 'thstrm_nm',
                 'frmtrm_nm', 'ord'],
                axis=1, inplace=True)
        df.columns = ['접수번호', '사업연도', '주식코드', '개별/연결구분', '재무제표구분',
                      '계정명', '당기일자', '당기금액', '전기일자', '전기금액',
                      '통화단위', "당기누적금액", "전기누적금액"]
        return df


class 단일회사주요계정_사업(단일회사주요계정):
    def __init__(self):
        super().__init__()

    def get_data(self, corp_code, year):
        df = super().get_raw_data(corp_code, year, "4Q")
        df.drop(["reprt_code", "corp_code", "fs_nm", 'sj_nm', 'thstrm_nm',
                 'frmtrm_nm', 'ord', 'bfefrmtrm_nm'],
                axis=1, inplace=True)
        df.columns = ['접수번호', '사업연도', '주식코드', '개별/연결구분', '재무제표구분',
                      '계정명', '당기일자', '당기금액', '전기일자', '전기금액',
                      '전전기일자', '전전기금액', '통화단위']
        return df

'''
00356370,00126380
'''
