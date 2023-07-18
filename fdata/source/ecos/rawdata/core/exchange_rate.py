from fdata.source.ecos.rawdata.core.core import 통계표조회


class 주요국통화의대원화환율(통계표조회):
    def __init__(self):
        super().__init__()
        self.stat_code = "731Y001"
        self.period_type = "일"


