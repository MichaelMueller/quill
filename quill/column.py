# builtin
from typing import Optional, Literal, Union, Type, Any
# 3rd party
import pydantic
# local
from quill.sql_expression import SqlExpression

class Column(SqlExpression):
    type:Literal["column"] = "column"
    
    name: str
    data_type: Union[Type[str], Type[int], Type[float], Type[bool], Type[bytes]]
    is_nullable: bool = False
    default: Optional[Union[str, int, float, bool, bytes]] = None

    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        sqlite_type = {
            str: "TEXT",
            int: "INTEGER",
            float: "REAL",
            bool: "BOOLEAN",
            bytes: "BLOB"
        }.get(self.data_type)
        args = []
        sql = f"{self.name} {sqlite_type}"
        if self.name == "id":
            sql += " PRIMARY KEY AUTOINCREMENT"
        else:
            if not self.is_nullable:
                sql += " NOT NULL"
            if self.default is not None:
                sql += f" DEFAULT ?"
                args.append(self.default)
        return sql, args
  