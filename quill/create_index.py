# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.manage_index import ManageIndex

class CreateIndex(ManageIndex):
    type:Literal["create_index"] = "create_index"
    if_not_exists: bool = False
    
    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        index_name = self._index_name()

        sql = "CREATE "
        if self.unique:
            sql += "UNIQUE "
        sql += "INDEX "
        if self.if_not_exists:
            sql += "IF NOT EXISTS "
        sql += index_name + " ON " + self.table_name + " ("
        sql += ", ".join(self.columns)
        sql += ")"
        return sql, []