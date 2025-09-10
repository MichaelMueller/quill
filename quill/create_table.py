# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.write_operation import WriteOperation
from quill.column import Column
from quill.sql_expression import IDENTIFIER_REGEX

class CreateTable(WriteOperation):
    type:Literal["create_table"] = "create_table"
    columns: list[Column]
    if_not_exists: bool = False

    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        SQLITE_TYPE_MAP = {
            str: "TEXT",
            int: "INTEGER",
            float: "REAL",
            bool: "INTEGER",  # SQLite does not have a separate Boolean storage class
            bytes: "BLOB",
        }
        # Build CREATE TABLE statement and parameters from CreateTableData
        sql = "CREATE TABLE "
        if self.if_not_exists:
            sql += "IF NOT EXISTS "
        sql += self.table_name + " ("
        params = []
        cols = self.columns.copy()
        cols.insert(0, Column(name="id", data_type="int"))
        for i, col in enumerate(cols):
            col_sql, col_params = col.to_sqlite_sql()
            sql += (", " if i > 0 else "") + col_sql
            params.extend(col_params)
        sql += ")"
        return sql, params