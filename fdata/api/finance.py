import fdata.db.api as db

def get_capital_amount(stock_name):
    obj = db.finance.StockBS()
    df = obj.read_db(stock_name,["사업연도", "계정명", "당기금액"])
    df = df[df.계정명 == "자본총계"]
    df.drop("계정명", axis=1, inplace=True)
    df.columns = ["사업연도", stock_name]

    return df
