# builtin
from typing import Any, Literal
# 3rd party
import pydantic
# local
from quill.write_operation import WriteOperation
from quill.column import Column

class RenameTable(WriteOperation):
    type:Literal["rename_table"] = "rename_table"
    old_table_name: str
    new_table_name: str
        
    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        sql = f"ALTER TABLE {self.old_table_name} RENAME TO {self.new_table_name}"
        return sql, []