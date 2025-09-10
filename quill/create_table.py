# builtin
from typing import Optional, Any
# 3rd party
import pydantic
# local
from quill.data.create_table import CreateTable as CreateTableData
from quill.column import Column, ColumnData
from quill.expression import Expression

class CreateTable(Expression):
    
    def __init__(self, data:CreateTableData):
        self._data = data
        
    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        sql = f"CREATE TABLE "
        params: list[Any] = []
        if self._data.if_not_exists:
            sql += "IF NOT EXISTS "
        sql += f"{self._data.table_name} ("
        col_defs = []
        cols = self._data.columns.copy()
        cols.insert(0, ColumnData(name="id", data_type=int, is_nullable=False))
        for col_data in cols:
            col_sql, col_params = Column( col_data ).to_sqlite_sql()
            col_defs.append(col_sql)
            params.extend(col_params)
        sql += ", ".join(col_defs)
        sql += ")"
        return sql, params