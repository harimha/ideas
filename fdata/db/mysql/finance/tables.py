import time
import fdata.source.dart.api as dart
from fdata.db.mysql.utils.utils import read_db
from fdata.db.mysql.base.schemas import Finance
from fdata.db.mysql.finance.mixin import CrossSectional, TimeSeries



class CorpCode(Finance, CrossSectional):
    def __init__(self):
        super().__init__()
        self.table_name = "corp_code"
        self.columns = ['corp_code', 'corp_name', 'stock_code', 'modify_date']
        self.types = ['varchar(20)', 'varchar(100)', 'varchar(20)', 'varchar(20)']
        self.pkey = ["corp_code"]
        self.create_table()
        self.get_data = dart.get_corp_code
        self.table_obj = self.get_table_obj()


class StockBS(Finance, TimeSeries):
    def __init__(self):
        super().__init__()
        self.table_name = "stock_bs"
        self.columns = ['사업연도', '접수일자', '주식코드', '계정명', '당기일자',
                        '당기금액', '통화단위']
        self.types = ['varchar(10)', 'datetime', 'varchar(10)', 'varchar(50)', 'datetime',
                      'bigint', 'varchar(10)']
        self.pkey = ["사업연도", "주식코드", "계정명"]
        self.create_table()
        self.get_data = dart.get_fs_bs
        self.table_obj = self.get_table_obj()


class StockIS(Finance, TimeSeries):
    def __init__(self):
        super().__init__()
        self.table_name = "stock_is"
        self.columns = ['사업연도', '접수일자', '주식코드', '계정명', '당기금액',
                        '통화단위', '시작일', '종료일']
        self.types = ['varchar(10)', 'datetime', 'varchar(10)', 'varchar(50)', 'bigint',
                      'varchar(10)', 'datetime', 'datetime']
        self.pkey = ["사업연도", "주식코드", "계정명"]
        self.create_table()
        self.get_data = dart.get_fs_is
        self.table_obj = self.get_table_obj()

