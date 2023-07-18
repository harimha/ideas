import time
import pandas as pd
from typing import overload
from datetime import timedelta
from sqlalchemy import update, select
from fdata.db.mysql.base.tables import TableOperation
from fdata.db.mysql.utils.utils import split_period, is_within_one_year, hasNull
from fdata.utils.datetimes import date_format, get_last_buisiness_day


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

    @overload
    def store_data(self):
        ...
    @overload
    def store_data(self, stock_name, search_date):
        ...

    def store_data(self, *args):
        if len(args)==2:
            stock_name, search_date = args
            df_data = self.get_data(stock_name, search_date)
        else:
            df_data = self.get_data()
        df_data = df_data[self.columns]
        df_db = self.read_db(self.columns)
        self.df_to_db(df_data, df_db)


class TimeSeries(TableOperation):
    def __init__(self):
        super().__init__()

    def read_db(self, stock_name, columns, sdate=None, edate=None):
        tbo = self.get_table_obj()
        if isinstance(columns, list):
            columns = tuple(columns)
        if (sdate == None) & (edate == None) :
            stmt = select(tbo.c[columns]).where(tbo.c["stock_name"]==stock_name)
        else:
            stmt = select(tbo.c[columns]).where(tbo.c["stock_name"]==stock_name,
                                                tbo.c["일자"].between(sdate, edate))
        df = pd.read_sql(stmt,self.engine)

        return df


    def store_data_period_naver(self, stock_name, sdate, edate):
        df_data = self.get_data(stock_name, sdate, edate)
        df_data = df_data[self.columns]
        df_db = self.read_db(stock_name, self.columns)
        self.df_to_db(df_data, df_db)


    def store_data_period_krx(self, stock_name, sdate, edate, sleep_time=0.1, **kwargs):
        '''
        kwargs : adj_price:bool
        krx에서 2년 조회 기간 제한에 대한 사용
        '''
        if is_within_one_year(sdate, edate):
            try:
                df_data = self.get_data(stock_name, sdate, edate, **kwargs)
                df_data = df_data[self.columns]
                df_db = self.read_db(stock_name, self.columns, sdate, edate)
                self.df_to_db(df_data, df_db)
                sdate, edate = date_format(sdate, edate)
                print(f"{stock_name} is stored {format(sdate, '%Y-%m-%d')}~{format(edate, '%Y-%m-%d')}")
            except:
                sdate, edate = date_format(sdate, edate)
                print(f"{stock_name} is empty {format(sdate, '%Y-%m-%d')}~{format(edate, '%Y-%m-%d')}")
        else:
            date_list = split_period(sdate, edate, interval=365)
            for sdate, edate in date_list:
                time.sleep(sleep_time)
                try:
                    df_data = self.get_data(stock_name, sdate, edate, **kwargs)
                    df_data = df_data[self.columns]
                    df_db = self.read_db(stock_name, self.columns, sdate, edate)
                    self.df_to_db(df_data, df_db)
                    print(f"{stock_name} is stored {format(sdate, '%Y-%m-%d')}~{format(edate, '%Y-%m-%d')}")
                except:
                    print(f"{stock_name} is empty {format(sdate, '%Y-%m-%d')}~{format(edate, '%Y-%m-%d')}")

    # def modify_data(self, index_name, date, values):
    #     '''해당 날짜의 데이터 값 수정'''
    #     tbo = self.table_obj
    #     stmt = update(tbo).where((tbo.c["일자"] == date) &
    #                              (tbo.c["index_name"] == index_name)).values(values)
    #     self.commit_statement(stmt)
    #
    # def modify_df_to_db(self, index_name, df):
    #     '''dataframe 데이터를 입력받아 db에 업데이트'''
    #     for i in range(len(df)):
    #         date = df["일자"].iloc[i]
    #         values = df.iloc[i][1:8]
    #         self.modify_data(index_name, date, values)
    #
    # def update_data_period(self, index_name, sdate, edate, sleep_time=1.5):
    #     if is_within_one_year(sdate, edate):
    #         df = self.get_data(index_name, sdate, edate)
    #         self.modify_df_to_db(index_name, df)
    #         print(f"{sdate}~{edate}")
    #     else:
    #         date_list = split_period(sdate, edate, 365)
    #         for sdate, edate in date_list:
    #             df = self.get_data(index_name, sdate, edate)
    #             self.modify_df_to_db(index_name, df)
    #             print(f"{sdate}~{edate}")
    #             time.sleep(sleep_time)
    #
    # def update_db_uptodate(self, stock_name, sleep_time=1.5):
    #     edate = get_last_buisiness_day()
    #     sdate = self.read_db(stock_name, "일자").max()[0]
    #     if edate == sdate:
    #         print(f"{stock_name} is already up to date")
    #     else:
    #         self.store_data_period(stock_name, sdate+timedelta(1), edate, sleep_time)
