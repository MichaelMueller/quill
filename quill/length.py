# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.value_expression import ValueExpression
from quill.ref import Ref
from quill.sql_expression import SUPPORTED_DIALECTS

class Length(ValueExpression):
    type:Literal["length"] = "length"
    column: Ref

    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite", params:list[Any]=[]) -> str:
        sql = "LENGTH("
        sql += self.column.name + ")"
        return sql