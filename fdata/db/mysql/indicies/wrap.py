from fdata.db.indicies.utils import name_to_code


def get_code_from_db(func):
    def wrapper(self, index_name):
        try:
            full_code, short_code = name_to_code(index_name)
        except:
            full_code, short_code = func(self, index_name)
        return full_code, short_code
    return wrapper


