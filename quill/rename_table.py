# builtin
from typing import Any, Literal
# 3rd party
import pydantic
# local
from quill.write_operation import WriteOperation
from quill.sql_expression import IDENTIFIER_REGEX, SUPPORTED_DIALECTS

class RenameTable(WriteOperation):
    type:Literal["rename_table"] = "rename_table"
    new_table_name: str = pydantic.Field(..., pattern=IDENTIFIER_REGEX)
        
    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite") -> tuple[str, list[Any]]:
        sql = f"ALTER TABLE {self.table_name} RENAME TO {self.new_table_name}"
        return sql, []