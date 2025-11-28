# builtin
from typing import Literal, Any
# 3rd party
import pydantic
# local
from quill.condition import Condition
from quill.comparison import Comparison
from quill.sql_expression import SUPPORTED_DIALECTS

class Or(Condition):
    type:Literal["or"] = "or"
    items: list[Condition]
    
    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite", params:list[Any]=[]) -> str:
        sql = ""

        for i, item in enumerate(self.items):
            item_params = []
            item_sql = item.to_sql(dialect, item_params)
            sql += f"{item_sql}" if isinstance(item, Comparison) else f"({item_sql})"
            params.extend(item_params)
            if i < len(self.items) - 1:
                sql += " OR "

        return sql