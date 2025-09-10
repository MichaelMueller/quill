# builtin
from typing import Literal
# 3rd party
import pydantic
# local
from quill.condition import Condition
from quill.comparison import Comparison

class And(Condition):
    type:Literal["and"] = "and"
    items: list[Condition]
    
    def to_sqlite_sql(self):
        sql = ""
        params = []

        for i, item in enumerate(self.items):
            item_sql, item_params = item.to_sqlite_sql()
            sql += f"{item_sql}" if isinstance(item, Comparison) else f"({item_sql})"
            params.extend(item_params)
            if i < len(self.items) - 1:
                sql += " AND "

        return sql, params