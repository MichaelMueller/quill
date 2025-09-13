# builtin
from typing import Any, Literal
# 3rd party
import pydantic
# local
from quill.write_operation import WriteOperation
from quill.sql_expression import IDENTIFIER_REGEX, SUPPORTED_DIALECTS

class DropTable(WriteOperation):
    type:Literal["drop_table"] = "drop_table"
    if_exists: bool = False
    
    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite", params:list[Any]=[]) -> str:
        sql = f"DROP TABLE {'IF EXISTS' if self.if_exists else ''} {self.table_name}"
        return sql