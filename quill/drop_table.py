# builtin
from typing import Any, Literal
# 3rd party
import pydantic
# local
from quill.write_operation import WriteOperation
from quill.sql_expression import IDENTIFIER_REGEX

class DropTable(WriteOperation):
    type:Literal["drop_table"] = "drop_table"
    table: str = pydantic.Field(..., pattern=IDENTIFIER_REGEX)
    if_exists: bool = False
    
    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        sql = f"DROP TABLE {'IF EXISTS' if self.if_exists else ''} {self.table}"
        return sql, []