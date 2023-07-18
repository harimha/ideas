from fdata.db.stock.utils import name_to_code


def get_code_from_db(func):
    def wrapper(self, stock_name):
        try:
            full_code, short_code = name_to_code(stock_name)
        except:
            full_code, short_code = func(self, stock_name)
        return full_code, short_code
    return wrapper

