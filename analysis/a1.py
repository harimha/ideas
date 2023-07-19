import fdata.api as api
from fdata.source.dart.api.fs import get_fs_bs, get_fs_is

df = get_fs_is("삼성전자","2021","2Q", fs_div="개별")
df.head()
