# builtin
from typing import Literal
# 3rd party
import pydantic
# local
from quill.sql_expression import IDENTIFIER_REGEX
from quill.sql_query import SqlQuery

class WriteOperation(SqlQuery):
    table_name: str = pydantic.Field(..., pattern=IDENTIFIER_REGEX)