# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.value_expression import ValueExpression
from quill.sql_expression import IDENTIFIER_REGEX

class ColumnRef(ValueExpression):
    type:Literal["column_ref"] = "column_ref"
    table_name: Optional[str] = pydantic.Field(default=None, pattern=IDENTIFIER_REGEX)
    name: str = pydantic.Field(..., pattern=IDENTIFIER_REGEX)
    
    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        sql = ""
        params: list[Any] = []
        if self.table_name:
            sql += self.table_name + "."
        sql += self.name
        return sql, params