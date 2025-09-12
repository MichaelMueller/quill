# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.write_operation import WriteOperation
from quill.sql_expression import SUPPORTED_DIALECTS

class Delete(WriteOperation):
    type:Literal["delete"] = "delete"    
    ids: list[int]
    
    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite") -> tuple[str, list[Any]]:
        sql = f"DELETE FROM {self.table_name} WHERE id IN ({', '.join(['?' for _ in self.ids])})"
        params = self.ids
        return sql, params