from sqlalchemy import text
from pandas.api.types import is_list_like


def create_table(schema_name, table_name):
    stmt = text(f"CREATE TABLE {schema_name}.{table_name} (tmp int)") # 임시칼럼
    return stmt

def drop_table(schema_name, table_name):
    stmt = text(f"Drop TABLE {schema_name}.{table_name}")
    return stmt

def add_column(schema_name, table_name, col_name, type):
    stmt = text(f"ALTER TABLE {schema_name}.{table_name} ADD COLUMN {col_name} {type}")
    return stmt

def drop_column(schema_name, table_name, col_name):
    stmt = text(f"ALTER TABLE {schema_name}.{table_name} DROP COLUMN {col_name}")
    return stmt

def alter_constraint(schema_name, table_name, constraint, column_obj):
    col_name = column_obj.name
    col_type = column_obj.type
    stmt = text(f"ALTER TABLE {schema_name}.{table_name} CHANGE COLUMN {col_name} {col_name} {col_type} {constraint} ;")
    return stmt

def drop_primarykey(schema_name, table_name):
    stmt = text(f"ALTER TABLE {schema_name}.{table_name} DROP PRIMARY KEY")
    return stmt

def add_primarykey(schema_name, table_name, columns):
    if is_list_like(columns):
        key_col = ",".join(columns)
        stmt = text(f"ALTER TABLE {schema_name}.{table_name} ADD PRIMARY KEY ({key_col})")
    else:
        stmt = text(f"ALTER TABLE {schema_name}.{table_name} ADD PRIMARY KEY ({columns})")

    return stmt

def insert_into(schema_name, table_name, values):
    stmt = text(f"INSERT INTO {schema_name}.{table_name} VALUES {values}")
    return stmt


def add_partion_by_string_range(schema_name, table_name, column, partition_list):
    stmt_lst = []
    for i, v in enumerate(partition_list, 1):
        stmt_text = f"PARTITION p{i} VALUES LESS THAN ('{v}')"
        stmt_lst.append(stmt_text)
    partitions = ",".join(stmt_lst)
    stmt = text(f"alter table {schema_name}.{table_name} PARTITION BY RANGE COLUMNS({column})({partitions},PARTITION p{i+1} VALUES LESS THAN (MAXVALUE));")

    return stmt


