import time
import fdata.source.krx.api.stock as krx_stock
import fdata.source.naver.api.stock as naver_stock
from fdata.db.mysql.utils.utils import read_db
from fdata.db.mysql.base.schemas import Stock
from fdata.db.mysql.stock.mixin import CrossSectional, TimeSeries


class StockCode(Stock, CrossSectional):
    def __init__(self):
        super().__init__()
        self.table_name = "stock_code"
        self.columns = ['full_code', 'short_code', 'stock_name', 'market_code', 'market_name', 'market_eng_name']
        self.types = ['varchar(20)', 'varchar(30)', 'varchar(50)', 'varchar(30)', 'varchar(30)', 'varchar(30)']
        self.pkey = ["short_code"]
        self.create_table()
        self.get_data = krx_stock.get_stock_code
        self.table_obj = self.get_table_obj()


class StockBasicInfo(Stock, CrossSectional):
    def __init__(self):
        super().__init__()
        self.table_name = "stock_basic_info"
        self.columns = ['단축코드', '한글종목약명', '상장일', '시장구분', '증권구분',
                        '소속부', '주식종류']
        self.types = ['varchar(30)', 'varchar(30)', 'datetime', 'varchar(30)', 'varchar(30)',
                      'varchar(30)','varchar(30)']
        self.pkey = ["단축코드"]
        self.create_table()
        self.get_data = krx_stock.get_basic_info
        self.table_obj = self.get_table_obj()


class StockDetails(Stock, CrossSectional):
    def __init__(self):
        super().__init__()
        self.table_name = "stock_details"
        self.columns = ['종목코드', '종목명', '시장구분', '소속부', '상장특례',
                        '업종코드', '업종명', '결산월', '지정자문인', '상장주식수',
                        '액면가', '자본금', '통화구분', '주소']
        self.types = ['varchar(30)', 'varchar(30)', 'varchar(30)', 'varchar(30)', 'varchar(30)',
                      'varchar(30)','varchar(50)', 'varchar(30)', 'varchar(30)', 'bigint',
                      'float', 'bigint', 'varchar(30)', 'varchar(200)']
        self.pkey = ["종목코드"]
        self.create_table()
        self.get_data = krx_stock.get_listed_company_details
        self.table_obj = self.get_table_obj()


class StockOHLCV_NAVER(Stock, TimeSeries):
    def __init__(self):
        super().__init__()
        self.table_name = "stock_ohlcv_naver"
        self.columns = ['일자', '시가', '고가', '저가', '종가', '거래량', 'stock_name']
        self.types = ['datetime', 'int', 'int', 'int', 'int', 'bigint', 'varchar(50)']
        self.pkey = ["일자", "stock_name"]
        self.create_table()
        self.partion_list = self.get_partition_list(20)
        self.add_partition_by_string("stock_name", self.partion_list)
        self.get_data = naver_stock.get_stock_ohlcv
        self.table_obj = self.get_table_obj()

    def get_partition_list(self, n):
        df = read_db(self.schema_name, "stock_code", "stock_name")
        lst = super().get_partition_list(df, "stock_name", n)

        return lst


class StockOHLCV_KRX(Stock, TimeSeries):
    def __init__(self):
        super().__init__()
        self.table_name = "stock_ohlcv_krx"
        self.columns = ['일자', '종가', '시가', '고가', '저가',
                        '거래량', '거래대금', '시가총액', '상장주식수', 'stock_name']
        self.types = ['datetime', 'int', 'int', 'int', 'int',
                      'bigint', 'bigint', 'bigint', 'bigint', 'varchar(30)']
        self.pkey = ["일자", "stock_name"]
        self.create_table()
        self.get_data = krx_stock.get_stock_ohlcv
        self.table_obj = self.get_table_obj()


class StockPER_PBR_DIV(Stock, TimeSeries):
    def __init__(self):
        super().__init__()
        self.table_name = "stock_per_pbr_div"
        self.columns = ['일자', 'EPS', 'PER', 'BPS', 'PBR',
                        'DPS', 'DVD_YLD', 'stock_name']
        self.types = ['datetime', 'int', 'float', 'int', 'float',
                      'int', 'float', 'varchar(30)']
        self.pkey = ["일자","stock_name"]
        self.create_table()
        self.get_data = krx_stock.get_stock_PER_PBR_Div
        self.table_obj = self.get_table_obj()



class StockForeignHoldings(Stock, TimeSeries):
    def __init__(self):
        super().__init__()
        self.table_name = "stock_foreign_holdings"
        self.columns = ['일자', '상장주식수', '외국인보유수량', '외국인지분율', '외국인한도수량',
                        '외국인한도소진율', 'stock_name']
        self.types = ['datetime', 'bigint', 'bigint', 'float', 'bigint',
                      'float', 'varchar(30)']
        self.pkey = ["일자", "stock_name"]
        self.create_table()
        self.get_data = krx_stock.get_foreign_holdings_stock
        self.table_obj = self.get_table_obj()

