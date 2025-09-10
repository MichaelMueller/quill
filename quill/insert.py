# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.write_operation import WriteOperation

class Insert(WriteOperation):
    type:Literal["insert"] = "insert"
    values: dict[str, Optional[Any]]
        
    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        columns = ', '.join(self.values.keys())
        placeholders = ', '.join(['?' for _ in self.values])
        sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        params = list(self.values.values())
        return sql, params