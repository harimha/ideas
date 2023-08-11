from fdata.db.mysql.indicies.tables import IndexOHLCV, IndexInfo, IndexCode

def kospi_c(sdate=None, edate=None):
    obj = IndexOHLCV()
    df = obj.read_db("코스피", ["일자", "종가", "상장시가총액"], sdate, edate)

    return df

def kospi_sector_c(sdate=None, edate=None):
    obj = IndexOHLCV()
    df = obj.read_db("코스피", ["일자", "종가"], sdate, edate)
    df = df.set_index("일자").rename(columns={"종가":"코스피"})
    icode = IndexCode()
    code_df = icode.read_db(icode.columns)
    df_sector_index = code_df.loc[code_df["market_name"] == "KOSPI"][4:25]
    i_lst = list(df_sector_index["index_name"])
    # i_lst.remove("의료정밀")
    # i_lst.remove("전기가스업")
    # i_lst.remove("통신업")
    # i_lst.remove("서비스업")

    for index_name in i_lst:
        df2 = obj.read_db(index_name, ["일자", "종가"], sdate, edate)
        df2 = df2.set_index("일자").rename(columns={"종가": index_name})
        df = df.merge(df2, how="left", left_index=True, right_index=True)

    return df

