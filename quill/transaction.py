# builtin
from typing import Literal
# 3rd party
import pydantic
# local
from quill.query import Query
from quill.write_operation import WriteOperation

class Transaction(Query):
    type: Literal["transaction"] = "transaction"
    items: list[WriteOperation]
    
    def to_sqlite_sql(self) -> tuple[str, list]:
        sql, args = "", []
        for item in self.items:
            item_sql, item_args = item.to_sqlite_sql()
            sql += f"{item_sql}; "
            args.extend(item_args)

        return sql.strip(), args