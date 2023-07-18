from fdata.db.mysql.utils.utils import read_db


def _schema_table_name():
    schema_name = "stock"
    table_name = "stock_code"

    return schema_name, table_name

def name_to_code(stock_name):
    '''
    :param stock_name: 종목명
    :return: full_code, short_code
    '''
    schema_name, table_name = _schema_table_name()
    df = read_db(schema_name, table_name, ("full_code", "short_code", "stock_name"))
    cond = df["stock_name"] == stock_name
    full_code, short_code = tuple(df[["full_code", "short_code"]][cond].iloc[0])

    return full_code, short_code

def fcode_to_scode(full_code):
    schema_name, table_name = _schema_table_name()
    df = read_db(schema_name, table_name, ("full_code", "short_code"))
    cond = df["full_code"] == full_code
    short_code = df["short_code"][cond].iloc[0]

    return short_code

def scode_to_fcode(short_code):
    schema_name, table_name = _schema_table_name()
    df = read_db(schema_name, table_name, ("full_code", "short_code"))
    cond = df["short_code"] == short_code
    full_code = df["full_code"][cond].iloc[0]

    return full_code

def fcode_to_name(full_code):
    schema_name, table_name = _schema_table_name()
    df = read_db(schema_name, table_name, ("full_code", "stock_name"))
    cond = df["full_code"] == full_code
    stock_name = df["stock_name"][cond].iloc[0]

    return stock_name

def scode_to_name(short_code):
    schema_name, table_name = _schema_table_name()
    df = read_db(schema_name, table_name, ("short_code", "stock_name"))
    cond = df["short_code"] == short_code
    stock_name = df["stock_name"][cond].iloc[0]

    return stock_name


def get_listing_date(stock_name):
    '''
    :return: 주식 상장일 반환
    '''
    schema_name = "stock"
    table_name = "stock_basic_info"
    df = read_db(schema_name, table_name, ("한글종목약명", "상장일"))
    cond = df["한글종목약명"] == stock_name
    listing_date = df["상장일"][cond].iloc[0]

    return listing_date


