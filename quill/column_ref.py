# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.value_expression import ValueExpression

class ColumnRef(ValueExpression):
    type:Literal["column_ref"] = "column_ref"
    table_name: Optional[str] = None
    column_name: str
    
    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        sql = ""
        params: list[Any] = []
        if self.table_name:
            sql += self.table_name + "."
        sql += self.column_name
        return sql, params