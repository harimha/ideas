class Configuration():
    def _get_secret(self):
        secrets_dict = {}
        # with open("fdata/config/secret/secrets.txt", "r") as f:
        with open("./secret/secrets.txt", "r") as f:
            for line in f.readlines():
                key = line.strip().split("=", 1)[0].strip()
                val = line.strip().split("=", 1)[1].strip()
                secrets_dict[key] = val

        return secrets_dict


class MysqlConfig(Configuration):
    def __init__(self):
        self._secrets = self._get_secret()
        self._password = self._secrets["password"]
        self._base_server_path = self._secrets["base_server_path"]
        self._base_db_path = self._secrets["base_db_path"]
        self._mysqldump = self._base_server_path + "mysqldump"
        self._mysql = self._base_server_path + "mysql"
        self._user = self._secrets["user"]
        self._host = self._secrets["host"]
        self._port = self._secrets["port"]
        self._url = f"mysql://{self._user}:{self._password}@{self._host}"


class KosisConfig(Configuration):
    def __init__(self):
        self._secrets = self._get_secret()
        self._kosis_apikey = self._secrets["kosis_apikey"]


class FisisConfig(Configuration):
    def __init__(self):
        self._secrets = self._get_secret()
        self._fisis_apikey = self._secrets["fisis_apikey"]


class EcosConfig(Configuration):
    def __init__(self):
        self._secrets = self._get_secret()
        self._apikey = self._secrets["ecos_apikey"]

class DartConfig(Configuration):
    def __init__(self):
        self._secrets = self._get_secret()
        self._apikey = self._secrets["dart_apikey"]