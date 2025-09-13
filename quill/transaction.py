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
            item_sql, item_args = item.to_sql(dialect)
            sql += f"{item_sql}; "
            params.extend(item_args)

        return sql
    
    def find(self, table_name: str, operation_type: Optional[Type[WriteOperation]] = None) -> list[WriteOperation]:
        return [item for item in self.items if item.table_name == table_name and (operation_type is None or isinstance(item, operation_type))]