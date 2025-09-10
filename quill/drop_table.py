# builtin
from typing import Any, Literal
# 3rd party
import pydantic
# local
from quill.write_operation import WriteOperation
from quill.column import Column

class DropTable(WriteOperation):
    type:Literal["drop_table"] = "drop_table"
    table: str    
    if_exists: bool = False
    
    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        sql = f"DROP TABLE {'IF EXISTS' if self.if_exists else ''} {self.table}"
        return sql, []