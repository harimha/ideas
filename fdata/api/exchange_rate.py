from fdata.source.ecos.rawdata.subclass.exchange_rate import 원_미국달러


def won_dollar(sdate, edate):
    obj = 원_미국달러()
    df = obj.get_data_day(sdate, edate)

    return df
