# builtin
from typing import Literal
# 3rd party
import pydantic
# local
from quill.sql_expression import SqlExpression

class Condition(SqlExpression):
    type:Literal["condition"] = "condition"