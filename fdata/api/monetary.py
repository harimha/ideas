from fdata.source.ecos.rawdata.core.monetary import M2_상품별구성내역_평잔_원계열


def m2(smonth, emonth):
    obj = M2_상품별구성내역_평잔_원계열()
    df = obj.get_data_month(smonth, emonth)

    return df