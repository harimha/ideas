from fdata.source.ecos.rawdata.core.core import 통계표조회
from fdata.utils import dfhandling


class 본원통화_평잔_원계열(통계표조회):
    def __init__(self):
        super().__init__()
        self.stat_code = "102Y002"

    def get_data_month(self, smonth, emonth):
        period_type = "월"
        df = super()._get_data(self.stat_code, period_type, smonth, emonth)

        return df


class 본원통화_말잔_원계열(통계표조회):
    def __init__(self):
        super().__init__()
        self.stat_code = "102Y001"

    def get_data_month(self, smonth, emonth):
        period_type = "월"
        df = super()._get_data(self.stat_code, period_type, smonth, emonth)

        return df


class M2_상품별구성내역_평잔_원계열(통계표조회):
    def __init__(self):
        super().__init__()
        self.stat_code = "101Y004"

    def get_data_month_raw(self, smonth, emonth):
        period_type = "월"
        df = super()._get_data(self.stat_code, period_type, smonth, emonth)
        df = df[["시점", "통계항목명1", "값", "단위"]]
        df.columns = ["시점", "통계항목명", "값", "단위"]

        return df

    def get_data_month(self, smonth, emonth):
        # 시점과 발표일
        df = self.get_data_month_raw(smonth, emonth)
        df = df.apply(self._convert_month_to_date, axis=1)
        df = dfhandling.change_type(df, datetime="시점", float="값")
        df = df.apply(self._convert_currency_unit, axis=1)
        df.drop("단위", axis=1, inplace=True)

        df_merge = df[["시점"]][df["통계항목명"] == df["통계항목명"].unique()[0]]
        for i in range(len(df["통계항목명"].unique())):
            df_data = df[["시점", "값"]][df["통계항목명"] == df["통계항목명"].unique()[i]]
            df_data.columns = ["시점", df["통계항목명"].unique()[i]]
            df_merge = df_merge.merge(df_data, on="시점", how="left")

        return df_merge

class M2_상품별구성내역_말잔_원계열(통계표조회):
    def __init__(self):
        super().__init__()
        self.stat_code = "101Y002"
    pass


