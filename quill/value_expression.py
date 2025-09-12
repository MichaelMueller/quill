# builtin
from typing import Literal
# 3rd party
import pydantic
# local
from quill.sql_expression import SqlExpression

class ValueExpression(SqlExpression):
    type:Literal["ref"] = "ref"