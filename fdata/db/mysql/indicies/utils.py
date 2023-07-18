from fdata.db.mysql.utils.utils import read_db

def code_to_name(full_code, short_code):
    schema_name = "indicies"
    table_name = "index_code"
    df = read_db(schema_name, table_name, ("full_code", "short_code", "index_name"))
    cond1 = df["full_code"] == full_code
    cond2 = df["short_code"] == short_code
    index_name = df["index_name"][cond1 & cond2].iloc[0]

    return index_name

def name_to_code(index_name):
    schema_name = "indicies"
    table_name = "index_code"
    df = read_db(schema_name,table_name,("full_code", "short_code", "index_name"))
    cond = df["index_name"] == index_name
    full_code, short_code = tuple(df[["full_code", "short_code"]][cond].iloc[0])

    return full_code, short_code

def get_base_date(index_name):
    '''    
    :return: 지수 기준일 반환
    '''
    schema_name = "indicies"
    table_name = "index_info"
    df = read_db(schema_name, table_name, ("지수명", "기준일"))
    cond = df["지수명"] == index_name
    date = df["기준일"][cond].iloc[0]

    return date

def get_release_date(index_name):
    '''        
    :return: 지수 발표일 반환 
    '''
    schema_name = "indicies"
    table_name = "index_info"
    df = read_db(schema_name, table_name, ("지수명", "발표일"))
    cond = df["지수명"] == index_name
    date = df["발표일"][cond].iloc[0]

    return date
