# builtin
from typing import Literal, Any
# 3rd party
import pydantic
# local
from quill.condition import Condition
from quill.comparison import Comparison
from quill.sql_expression import SUPPORTED_DIALECTS

class And(Condition):
    type:Literal["and"] = "and"
    items: list[Condition]
    
    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite", params:list[Any]=[]) -> str:
        sql = ""

        for i, item in enumerate(self.items):
            item_sql, item_params = item.to_sql(dialect, params)
            sql += f"{item_sql}" if isinstance(item, Comparison) else f"({item_sql})"
            params.extend(item_params)
            if i < len(self.items) - 1:
                sql += " AND "

        return sql