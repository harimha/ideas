
def name_to_corpcode(corp_name):
    df = CorpCode.get_listed_corp()
    df = df["corp_code"].loc[df["corp_name"] == corp_name]
    corp_code = df.values[0]
    return corp_code

def corpcode_to_name(corp_code):
    df = CorpCode.get_listed_corp()
    df = df["corp_name"].loc[df["corp_code"] == corp_code]
    corp_name = df.values[0]
    return corp_name

def corpcode_to_stockcode(corp_code):
    df = CorpCode.get_listed_corp()
    df = df["stock_code"].loc[df["corp_code"] == corp_code]
    stock_code = df.values[0]
    return stock_code

def stockcode_to_corpcode(stockcode):
    df = CorpCode.get_listed_corp()
    df = df["corp_code"].loc[df["stock_code"] == stockcode]
    corp_code = df.values[0]
    return corp_code