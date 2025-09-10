# builtin
from typing import Optional, Literal
# 3rd party
import pydantic
# local
from quill.data.write_operation import WriteOperation
from quill.data.column import Column

class DropIndex(WriteOperation):
    type:Literal["drop_index"] = "drop_index"
    table_name: str
    columns: list[str]