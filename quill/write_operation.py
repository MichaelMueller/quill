# builtin
from typing import Literal
# 3rd party
import pydantic
# local
from quill.sql_expression import SqlExpression

class WriteOperation(SqlExpression):
    type:Literal["create_table", "drop_table", "rename_table", "create_index", "drop_index", "insert", "update", "delete"]