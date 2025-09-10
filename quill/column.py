# builtin
from typing import Optional, Literal, Union, Type, Any
# 3rd party
import pydantic
# local
from quill.sql_expression import SqlExpression, IDENTIFIER_REGEX

class Column(SqlExpression):
    type:Literal["column"] = "column"
    
    name: str = pydantic.Field(..., pattern=IDENTIFIER_REGEX)
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
            if self.default is not None or self.is_nullable:
                if type(self.default) == str or type(self.default) == bytes:
                    default_sql_value = f"'{self.default}'"
                    import sqlite3
                    conn = sqlite3.connect(":memory:")
                    escaped_value = conn.execute("SELECT quote(?)", (self.default,)).fetchone()[0]
                elif type(self.default) == bool:
                    default_sql_value = 1 if self.default else 0
                elif self.default == None:
                    default_sql_value = "NULL"
                else:
                    default_sql_value = self.default
                sql += f" DEFAULT {default_sql_value}"
        return sql, args
    