# builtin
from typing import Literal, Optional
# 3rd party
import pydantic
# local
from quill.sql_expression import SqlExpression

class Query(SqlExpression):
    model_config = {
        "extra": "allow",
    }

