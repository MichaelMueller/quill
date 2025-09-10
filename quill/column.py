# builtin
from typing import Optional, Any
# 3rd party
import pydantic
# local
from quill.data.column import Column as ColumnData
from quill.expression import Expression

class Column(Expression):
    
    def __init__(self, data:ColumnData):
        self._data = data
        
    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        sqlite_type = {
            str: "TEXT",
            int: "INTEGER",
            float: "REAL",
            bool: "BOOLEAN",
            bytes: "BLOB"
        }.get(self._data.data_type)
        args = []
        sql = f"{self._data.name} {sqlite_type}"
        if self._data.name == "id":
            sql += " PRIMARY KEY AUTOINCREMENT"
        else:
            if not self._data.is_nullable:
                sql += " NOT NULL"
            if self._data.default is not None:
                sql += f" DEFAULT ?"
                args.append(self._data.default)
        return sql, args