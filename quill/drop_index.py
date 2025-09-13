# builtin
from typing import Any, Literal
# 3rd party
import pydantic
# local
from quill.manage_index import ManageIndex
from quill.sql_expression import SUPPORTED_DIALECTS

class DropIndex(ManageIndex):
    type:Literal["drop_index"] = "drop_index"
    if_exists: bool = False
    
    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite") -> tuple[str, list[Any]]:
        index_name = self._index_name()
        if dialect == "mysql":
            sql = f"DROP INDEX {index_name} ON {self.table_name}"
        else:
            sql = f"DROP INDEX {'IF EXISTS' if self.if_exists else ''} {index_name}"
        return sql, []