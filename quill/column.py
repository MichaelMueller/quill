# builtin
from typing import Optional, Literal, Union, Type, Any
# 3rd party
import pydantic
# local
from quill.sql_expression import SqlExpression, IDENTIFIER_REGEX, SUPPORTED_DIALECTS

class Column(SqlExpression):
    type:Literal["column"] = "column"
    
    name: str = pydantic.Field(..., pattern=IDENTIFIER_REGEX)
    data_type: Literal["str", "int", "float", "bool", "bytes"]
    is_nullable: bool = False
    default: Optional[Union[str, int, float, bool, bytes]] = None
    max_length: Optional[int] = None

    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite", params:list[Any]=[]) -> str:
        
        if dialect == "postgres":
            type_map = {"str": "TEXT", "int": "INTEGER", "float": "DOUBLE PRECISION", "bool": "BOOLEAN", "bytes": "BYTEA"}
        elif dialect == "mysql":
            type_map = {"str": f"VARCHAR({self.max_length if self.max_length else 255})", "int": "INT", "float": "FLOAT", "bool": "TINYINT(1)", "bytes": "BLOB"}
        else:  # sqlite
            type_map = {"str": "TEXT","int": "INTEGER","float": "REAL","bool": "BOOLEAN","bytes": "BLOB"}
            
        type_ = type_map.get(self.data_type)
        if dialect == "postgres" and self.name == "id":
            type_ = "SERIAL"
        sql = f"{self.name} {type_}"
        
        if self.name == "id":
            if dialect == "postgres":
                sql += " PRIMARY KEY"
            elif dialect == "mysql":
                sql += " PRIMARY KEY AUTO_INCREMENT"
            else:
                sql += " PRIMARY KEY AUTOINCREMENT"
        else:
            if not self.is_nullable:
                sql += " NOT NULL"
            if self.default is not None or self.is_nullable:
                if type(self.default) == str or type(self.default) == bytes:
                    default_sql_value = f"'{self.default}'"
                    import sqlite3
                    try:
                        conn = sqlite3.connect(":memory:")
                        escaped_value = conn.execute("SELECT quote(?)", (self.default,)).fetchone()[0]
                        default_sql_value = escaped_value
                    finally:
                        conn.close()
                elif type(self.default) == bool:
                    default_sql_value = 1 if self.default else 0
                elif self.default == None:
                    default_sql_value = "NULL"
                else:
                    default_sql_value = self.default
                sql += f" DEFAULT {default_sql_value}"
        return sql
    