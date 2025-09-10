# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.value_expression import ValueExpression
from quill.column_ref import ColumnRef

class Length(ValueExpression):
    type:Literal["length"] = "length"
    column: ColumnRef

    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        sql = "LENGTH("
        sql += self.column.name + ")"
        params: list[Any] = []
        return sql, params