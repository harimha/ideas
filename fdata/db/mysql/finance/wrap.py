from fdata.db.mysql.stock.utils import name_to_code
from fdata.db.mysql.finance.utils import scode_to_ccode


def get_ccode_from_db(func):
    def wrapper(self, stock_name):
        try:
            scode = name_to_code(stock_name)[1]
            ccode = scode_to_ccode(scode)
        except:
            ccode = func(self, stock_name)
        return ccode
    return wrapper
