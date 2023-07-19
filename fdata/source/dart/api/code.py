from fdata.source.dart.rawdata.core import 고유번호

def get_corp_code():
    obj = 고유번호()
    df = obj.get_data()

    return df
