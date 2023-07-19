from fdata.db.mysql.stock.utils import name_to_code, scode_to_ccode, scode_to_name


def get_fscode_from_db(func):
    def wrapper(self, stock_name):
        try:
            full_code, short_code = name_to_code(stock_name)
        except:
            full_code, short_code = func(self, stock_name)
        return full_code, short_code
    return wrapper

