# builtin
from typing import Literal, Optional, Any
# 3rd party
import pydantic
# local
from quill.sql_expression import SqlExpression, SUPPORTED_DIALECTS

class SqlQuery(SqlExpression):
    pass
