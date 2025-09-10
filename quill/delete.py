# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.write_operation import WriteOperation

class Delete(WriteOperation):
    type:Literal["delete"] = "delete"    
    table_name: str
    ids: list[int]
    
    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        sql = f"DELETE FROM {self.table_name} WHERE id IN ({', '.join(['?' for _ in self.ids])})"
        params = self.ids
        return sql, params