class EmptyDataFrame(Exception):
    def __str__(self):
        return "DataFrame is Empty"

class WebResponseError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return f"{self.code} : {self.message}"

class DBNotFoundError(Exception):
    def __str__(self):
        return "DataBase is not found"