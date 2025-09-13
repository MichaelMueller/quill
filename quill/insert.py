# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.write_operation import WriteOperation
from quill.sql_expression import SUPPORTED_DIALECTS

class Insert(WriteOperation):
    type:Literal["insert"] = "insert"
    values: dict[str, Optional[Any]]
        
    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite", params:list[Any]=[]) -> str:
        columns = ', '.join(self.values.keys())
        placeholder_str = ""
        for value in self.values.values():
            placeholder_str += f"{", " if placeholder_str != "" else ""}{self.next_placeholder(dialect, params)}"
            params.append(value)
        sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholder_str})"
        return sql