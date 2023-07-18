from fdata.config.config import MysqlConfig
from sqlalchemy import create_engine, MetaData


class MySQL(MysqlConfig):
    def __init__(self):
        super().__init__()
        self.engine = create_engine(self._url)
        self.metadata = MetaData()

    def commit_statement(self, stmt):
        with self.engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()



