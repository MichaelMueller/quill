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
    
    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite", params:list[Any]=[]) -> str:
        
        sub_sql = ""
        for id in self.ids:
            sub_sql += f"{", " if sub_sql != "" else ""}{self.next_placeholder(dialect, params)}"
            params.append(id)
        sql = f"DELETE FROM {self.table_name} WHERE id IN ({sub_sql})"
        return sql