# builtin
from typing import Literal, Optional, Type,Any
# 3rd party
import pydantic
# local
from quill.query import Query
from quill.write_operation import WriteOperation
from quill.sql_expression import SUPPORTED_DIALECTS

class Transaction(Query):
    type: Literal["transaction"] = "transaction"
    items: list[WriteOperation]
    
    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite") -> tuple[str, list]:
        sql, args = "", []
        for item in self.items:
            item_sql, item_args = item.to_sql()
            sql += f"{item_sql}; "
            args.extend(item_args)

        return sql.strip(), args
    
    
    def to_postgres_sql(self) -> tuple[str, list[Any]]:
        return self.to_sql()

    def find(self, table_name: str, operation_type: Optional[Type[WriteOperation]] = None) -> list[WriteOperation]:
        return [item for item in self.items if item.table_name == table_name and (operation_type is None or isinstance(item, operation_type))]