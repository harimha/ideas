from fdata.db.mysql.indicies.tables import IndexOHLCV

def kospi_c(sdate=None, edate=None):
    obj = IndexOHLCV()
    df = obj.read_db("코스피", ["일자", "종가", "상장시가총액"], sdate, edate)

    return df
