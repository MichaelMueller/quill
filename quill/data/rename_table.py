# builtin
from typing import Optional, Literal
# 3rd party
import pydantic
# local
from quill.data.write_operation import WriteOperation
from quill.data.column import Column

class RenameTable(WriteOperation):
    type:Literal["rename_table"] = "rename_table"
    old_table_name: str
    new_table_name: str