# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.query import Query
from quill.condition import Condition

class Select(Query):
    type: str = "select"
    table_names: list[str]
    columns: list[str]
    where: Optional[Condition] = None
    
    limit: Optional[int] = None
    offset: Optional[int] = None
    
    order_by: Optional[str] = None
    order:Optional[Literal["asc","desc"]] = "asc"
                
    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        # Build SELECT statement and parameters from SelectData
        sql = "SELECT " + ", ".join(self.columns)
        sql += " FROM " + ", ".join(self.table_names)
        params = []
        if self.where:
            where_sql, where_params = self.where.to_sqlite_sql()
            sql += " WHERE " + where_sql
            params.extend(where_params)
        if self.order_by:
            sql += " ORDER BY " + self.order_by + " " + self.order
        if self.limit is not None:
            sql += " LIMIT ?"
            params.append(self.limit)
        if self.offset is not None:
            sql += " OFFSET ?"
            params.append(self.offset)
        return sql, params