from fdata.db.mysql.utils.utils import read_db


def scode_to_ccode(stock_code):
    schema_name = "finance"
    table_name = "corp_code"
    df = read_db(schema_name, table_name, ("stock_code", "corp_code"))
    cond = df["stock_code"] == stock_code
    corp_code = df["corp_code"][cond].iloc[0]

    return corp_code
