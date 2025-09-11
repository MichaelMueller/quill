# builtin
from typing import Literal, Optional
# 3rd party
import pydantic
# local
from quill.sql_expression import SqlExpression

class Query(SqlExpression):
    model_config = {
        "extra": "allow",
    }

    def affects_table(self, table_name:str) -> bool:
        if hasattr(self, "table_name"):
            affected_tables = [getattr(self, "table_name")]
        elif hasattr(self, "table_names"):
            affected_tables = getattr(self, "table_names")
        
        return table_name in affected_tables