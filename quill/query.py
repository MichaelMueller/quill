# builtin
from typing import Literal, Optional
# 3rd party
import pydantic
# local
from quill.sql_expression import SqlExpression

class Query(SqlExpression):
    token: Optional[str] = None # an arbitrary token that can be used to identify the user