# builtin
from typing import Literal
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
    
    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite"):
        sql = ""
        params = []
        
        left_sql, left_params = self.left.to_sql()
        sql += left_sql + " " + self.operator + " "
        params.extend(left_params)
        
        if isinstance(self.right, ValueExpression):
            right_sql, right_params = self.right.to_sql()
            sql += right_sql
            params.extend(right_params)
        elif isinstance(self.right, list):
            placeholders = ", ".join(["?"] * len(self.right))
            sql += f"({placeholders})"
            params.extend(self.right)
        else:
            sql += "?"
            params.append(self.right)
        return sql, params