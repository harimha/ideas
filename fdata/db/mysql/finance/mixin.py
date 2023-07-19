import time
import pandas as pd
from datetime import timedelta
from sqlalchemy import update, select
from fdata.db.mysql.base.tables import TableOperation
from fdata.db.mysql.utils.utils import split_period, is_within_one_year, hasNull
from fdata.utils.datetimes import date_format, get_last_buisiness_day
from fdata.db.mysql.stock.utils import name_to_code


class CrossSectional(TableOperation):
    def __init__(self):
        super().__init__()

    def read_db(self, columns):
        if isinstance(columns, list):
            columns = tuple(columns)
        tbo = self.get_table_obj()
        stmt = select(tbo.c[columns])
        df = pd.read_sql(stmt, self.engine)

        return df

    def store_data(self):
        df_data = self.get_data()
        df_data = df_data[self.columns]
        df_db = self.read_db(self.columns)
        self.df_to_db(df_data, df_db)


class TimeSeries(TableOperation):
    def __init__(self):
        super().__init__()

    def read_db(self, stock_name, columns, syear=None, eyear=None):
        tbo = self.get_table_obj()
        scode = name_to_code(stock_name)[1]
        if isinstance(columns, list):
            columns = tuple(columns)
        if (syear == None) & (eyear == None) :
            stmt = select(tbo.c[columns]).where(tbo.c["주식코드"]==scode)
        else:
            stmt = select(tbo.c[columns]).where(tbo.c["주식코드"]==scode,
                                                tbo.c["사업연도"].between(syear, eyear))
        df = pd.read_sql(stmt, self.engine)

        return df


    def store_data_period(self, stock_name, syear, eyear, quarter="4Q", fs_div="연결"):
        for year in range(int(syear), int(eyear)+1,1 ):
            try:
                df_data = self.get_data(stock_name, str(year), quarter, fs_div)
                df_data = df_data[self.columns]
                df_db = self.read_db(stock_name, self.columns)
                self.df_to_db(df_data, df_db)
                print(f'{year} {stock_name} is stored')
            except:
                continue
