# builtin
from typing import Optional, Literal, Any, List, Tuple
# 3rd party
import pydantic
# local
from quill.sql_query import SqlQuery
from quill.condition import Condition
from quill.sql_expression import SUPPORTED_DIALECTS

class Select(SqlQuery):
    type: str = "select"
    table_names: list[str]
    columns: Optional[list[str]] = None
    where: Optional[Condition] = None
    
    limit: Optional[int] = None
    offset: Optional[int] = None
    
    order_by:Optional[ List[ Tuple[ str, Literal["asc","desc"] ] ] ] = None
    
    as_dict: bool = False
                
    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite", params:list[Any]=[]) -> str:
        # Build SELECT statement and parameters from SelectData
        sql = "SELECT " + ( ", ".join(self.columns) if self.columns else "*" )
        sql += " FROM " + ", ".join(self.table_names)
        if self.where:
            where_params = []
            where_sql = self.where.to_sql(dialect, where_params)
            sql += " WHERE " + where_sql
            params.extend(where_params)
        if self.order_by:
            for i, (col, order) in enumerate(self.order_by):
                if i == 0:
                    sql += f" ORDER BY {col} {order}"
                else:
                    sql += f", {col} {order}"
            
        if dialect == "mysql" and self.offset is not None and self.limit is None:
            raise ValueError("MySQL requires LIMIT when OFFSET is specified")
        if self.limit is not None:
            sql += f" LIMIT {self.next_placeholder(dialect, params)}"
            params.append(self.limit)
        if self.offset is not None:
            sql += f" OFFSET {self.next_placeholder(dialect, params)}"
            params.append(self.offset)
            
        return sql