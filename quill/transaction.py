# builtin
from typing import Literal, Optional, Type,Any
# 3rd party
import pydantic
# local
from quill.sql_query import SqlQuery
from quill.write_operation import WriteOperation
from quill.sql_expression import SUPPORTED_DIALECTS

class Transaction(SqlQuery):
    type: Literal["transaction"] = "transaction"
    items: list[WriteOperation]
    
    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite", params:list[Any]=[]) -> str:
        sql = ""
        for item in self.items:
            item_args = []
            item_sql = item.to_sql(dialect, item_args)
            sql += f"{item_sql};"
            params.extend(item_args)

        return sql