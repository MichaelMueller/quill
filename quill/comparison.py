# builtin
from typing import Literal, Any
# 3rd party
import pydantic
# local
from quill.condition import Condition
from quill.value_expression import ValueExpression
from quill.sql_expression import SUPPORTED_DIALECTS

class Comparison(Condition):
    type:Literal["comparison"] = "comparison"
    
    operator: Literal["=", "!=", "<", "<=", ">", ">=", "LIKE", "IN", "IS", "IS NOT"]
    left: ValueExpression
    right: ValueExpression | int | list[int] | str | list[str] | float | list[float] | bool | None
    
    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite", params:list[Any]=[]) -> str:
        sql = ""
        
        left_params = []
        left_sql = self.left.to_sql(dialect, left_params)
        sql += left_sql + " " + self.operator + " "
        params.extend(left_params)
        
        if isinstance(self.right, ValueExpression):
            right_params = []
            right_sql = self.right.to_sql(dialect, right_params)
            sql += right_sql
            params.extend(right_params)
        elif isinstance(self.right, list):
            sub_sql = ""
            for value in self.right:
                sub_sql += f"{", " if sub_sql != "" else ""}{self.next_placeholder(dialect, params)}"
                params.append(value)
            sql += f"({sub_sql})"
        else:
            sql += self.next_placeholder(dialect, params)
            params.append(self.right)
        return sql