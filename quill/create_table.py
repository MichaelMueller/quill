# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.write_operation import WriteOperation
from quill.column import Column
from quill.sql_expression import IDENTIFIER_REGEX, SUPPORTED_DIALECTS

class CreateTable(WriteOperation):
    type:Literal["create_table"] = "create_table"
    columns: list[Column]
    if_not_exists: bool = False

    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite") -> tuple[str, list[Any]]:
                        
        # Build CREATE TABLE statement and parameters from CreateTableData
        sql = "CREATE TABLE "
        if self.if_not_exists:
            sql += "IF NOT EXISTS "
        sql += self.table_name + " ("
        params = []
        cols = self.columns.copy()
        cols.insert(0, Column(name="id", data_type="int"))
        for i, col in enumerate(cols):
            col_sql, col_params = col.to_sql(dialect)
            sql += (", " if i > 0 else "") + col_sql
            params.extend(col_params)
        sql += ");" if dialect != "mysql" else ") ENGINE=InnoDB;"
        return sql, params