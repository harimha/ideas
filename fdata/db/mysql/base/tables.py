import pandas as pd
import fdata.db.mysql.utils.statements as stmts
from sqlalchemy import inspect, MetaData
from fdata.db.mysql.base.engine import MySQL
from fdata.db.mysql.utils.utils import get_partition_list

class Table(MySQL):
    def __init__(self):
        super().__init__()

    def _isTableExists(self, schema_name, table_name):
        insp = inspect(self.engine)
        table_names = insp.get_table_names(schema_name)
        if table_name in table_names:
            return True
        else:
            return False

    def _isColumnExists(self, schema_name, table_name, col_name):
        insp = inspect(self.engine)
        columns = insp.get_columns(table_name, schema_name)
        col_names = []
        for col in columns:
            col_names.append(col["name"])
        if col_name in col_names:
            return True
        else:
            return False

    def create_table(self, schema_name, table_name):
        '''임시칼럼 tmp 생성됨'''
        if self._isTableExists(schema_name, table_name):
            pass
        else:
            stmt = stmts.create_table(schema_name, table_name)
            self.commit_statement(stmt)

    def drop_table(self, schema_name, table_name):
        if self._isTableExists(schema_name, table_name):
            stmt = stmts.drop_table(schema_name, table_name)
            self.commit_statement(stmt)
        else: pass

    def add_column(self, schema_name, table_name, col_name, col_type):
        if self._isColumnExists(schema_name, table_name, col_name):
            pass
        else:
            stmt = stmts.add_column(schema_name, table_name, col_name, col_type)
            self.commit_statement(stmt)

    def drop_column(self, schema_name, table_name, col_name):
        if self._isColumnExists(schema_name, table_name, col_name):
            stmt = stmts.drop_column(schema_name, table_name, col_name)
            self.commit_statement(stmt)
        else: pass

    def alter_constraint(self, schema_name, table_name, constraint, col_obj):
        '''
        UNIQUE, NOT NULL, CHECK, DEFAULT, AUTO_INCREMENT, ENUM 등 사용
        ex) alter_constraint(table_name, "not null", 'full_code')
        '''
        stmt = stmts.alter_constraint(schema_name, table_name, constraint, col_obj)
        self.commit_statement(stmt)

    def drop_primarykey(self, schema_name, table_name):
        stmt = stmts.drop_primarykey(schema_name, table_name)
        self.commit_statement(stmt)

    def add_primarykey(self, schema_name, table_name, columns:str or list):
        '''
        ex) add_primarykey(schema_name, table_name, ["col1","col2"])
        add_primarykey(schema_name, table_name, "col1")
        :param columns: str or list_like type
        '''
        stmt = stmts.add_primarykey(schema_name, table_name, columns)
        self.commit_statement(stmt)

    def insert_data(self, table_obj, values:pd.Series):
        stmt = insert(table_obj).values(values)
        self.commit_statement(stmt)

    def get_table_obj(self, schema_name, table_name):
        self.metadata = MetaData(schema_name)
        self.metadata.reflect(self.engine)
        table_obj = self.metadata.tables[f"{schema_name}.{table_name}"]

        return table_obj

    def get_column_obj(self, schema_name, table_name, col_name):
        self.metadata = MetaData(schema_name)
        self.metadata.reflect(self.engine)
        column_obj = self.metadata.tables[f"{schema_name}.{table_name}"].c[col_name]

        return column_obj

    def add_partition_by_string(self, schema_name, table_name, col_name, partition_list):
        stmt = stmts.add_partion_by_string_range(schema_name, table_name, col_name, partition_list)
        self.commit_statement(stmt)

    def get_partition_list(self, df, column_name, n):
        part_list = get_partition_list(df, column_name, n)

        return part_list


class TableOperation(Table):
    def __init__(self):
        super().__init__()

    def create_table(self):
        super().create_table(self.schema_name, self.table_name)
        if self._isColumnExists(self.schema_name, self.table_name, "tmp"):
            col_type = dict(zip(self.columns, self.types))
            for col_name, col_type in col_type.items():
                self.add_column(col_name, col_type)
            self.drop_column("tmp")  # 임시 칼럼 삭제
            try:
                self.drop_primarykey()
            except:
                pass
            try:
                self.add_primarykey(self.pkey)
            except:
                pass
        else: pass

    def drop_table(self):
        super().drop_table(self.schema_name, self.table_name)

    def add_column(self, col_name, col_type):
        super().add_column(self.schema_name, self.table_name, col_name, col_type)

    def drop_column(self, col_name):
        super().drop_column(self.schema_name, self.table_name, col_name)

    def alter_constraint(self, constraint, col_obj):
        '''
        UNIQUE, NOT NULL, CHECK, DEFAULT, AUTO_INCREMENT, ENUM 등 사용
        ex) alter_constraint(table_name, "not null", 'full_code')
        '''
        super().alter_constraint(self.schema_name, self.table_name, constraint, col_obj)

    def drop_primarykey(self):
        super().drop_primarykey(self.schema_name, self.table_name)

    def add_primarykey(self, columns: str or list):
        '''
        ex) add_primarykey(schema_name, table_name, ["col1","col2"])
        add_primarykey(schema_name, table_name, "col1")
        :param columns: str or list_like type
        '''
        super().add_primarykey(self.schema_name, self.table_name, columns)

    def insert_data(self, values: pd.Series):
        super().insert_data(self.table_obj, values)

    def get_table_obj(self):
        table_obj = super().get_table_obj(self.schema_name, self.table_name)

        return table_obj

    def get_column_obj(self, col_name):
        col_obj = super().get_column_obj(self.schema_name, self.table_name, col_name)

        return col_obj

    def get_df_to_update(self, df_data, df_db):
        merge_df = df_data.merge(df_db, how="left", indicator=True)
        df_to_update = merge_df.loc[lambda x: x["_merge"] == 'left_only'].drop('_merge', axis=1)

        return df_to_update

    def df_to_db(self, df_data, df_db):
        df_new = self.get_df_to_update(df_data, df_db)
        df_new.to_sql(self.table_name, self.engine, self.schema_name, index=False, if_exists='append')

    def add_partition_by_string(self, col_name, partition_list):
        if self._isTableExists(self.schema_name, self.table_name):
            pass
        else:
            super().add_partition_by_string(self.schema_name, self.table_name, col_name, partition_list)

