from fdata.source.ecos.rawdata.core.exchange_rate import 주요국통화의대원화환율
from fdata.utils import dfhandling


class 원_미국달러(주요국통화의대원화환율):
    def __init__(self):
        super().__init__()
        self.itemcode1 = "0000001"

    def get_data_day(self, sdate, edate):
        df = super()._get_data(self.stat_code, self.period_type, sdate, edate, self.itemcode1)
        df = df[["시점", "값"]]
        df.columns = ["일자", "원/달러"]
        col_datetime = ["일자"]
        col_float = ["원/달러"]
        df = dfhandling.change_type(df,
                                    datetime=col_datetime,
                                    float=col_float)

        return df


class 원_일본엔(주요국통화의대원화환율):
    def __init__(self):
        super().__init__()
        self.itemcode1 = "0000002"

    def get_data_day(self, sdate, edate):
        df = super()._get_data(self.stat_code, self.period_type, sdate, edate, self.itemcode1)
        df = df[["시점", "값"]]
        df.columns = ["일자", "원/100엔"]
        col_datetime = ["일자"]
        col_float = ["원/100엔"]
        df = dfhandling.change_type(df,
                                    datetime=col_datetime,
                                    float=col_float)
        return df



class 주요국통화의대미달러환율():
    def __init__(self):
        self.stat_code = "731Y002"
        self.period_type = "일"
