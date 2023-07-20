import fdata.api as api
import fdata.db.api as db

obj = db.finance.StockIS()
df = obj.read_db("삼성전자", obj.columns)
df[df["계정명"]=="당기순이익"]