from fdata.db.mysql.base.engine import MySQL
from sqlalchemy import inspect, schema, insert


class Schema(MySQL):
    def __init__(self):
        super().__init__()

    def _isSchemaExists(self, engine, schema_name):
        insp = inspect(engine)
        schema_names = insp.get_schema_names()
        if schema_name in schema_names:
            return True
        else:
            return False

    def create_schema(self, schema_name):
        if self._isSchemaExists(self.engine, schema_name):
            pass
        else:
            stmt = schema.CreateSchema(schema_name)
            self.commit_statement(stmt)

    def drop_schema(self, schema_name):
        if self._isSchemaExists(self.engine,schema_name):
            stmt = schema.DropSchema(schema_name)
            self.commit_statement(stmt)
        else:
            pass


class SchemaOperation(Schema):
    def __init__(self):
        super().__init__()

    def create_schema(self):
        super().create_schema(self.schema_name)

    def drop_schema(self, schema_name=None):
        super().drop_schema(self.schema_name)


class Indicies(SchemaOperation):
    def __init__(self):
        super().__init__()
        self.schema_name = "indicies"
        self.metadata.schema = self.schema_name
        self.create_schema()


class Stock(SchemaOperation):
    def __init__(self):
        super().__init__()
        self.schema_name = "stock"
        self.metadata.schema = self.schema_name
        self.create_schema()


class Finance(SchemaOperation):
    def __init__(self):
        super().__init__()
        self.schema_name = "finance"
        self.metadata.schema = self.schema_name
        self.create_schema()