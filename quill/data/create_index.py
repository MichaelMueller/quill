# builtin
from typing import Optional, Literal
# 3rd party
import pydantic
# local
from quill.data.write_operation import WriteOperation
from quill.data.column import Column

class CreateIndex(WriteOperation):
    type:Literal["create_index"] = "create_index"
    table_name: str
    columns: list[str]
    if_not_exists: bool = False
    unique: bool = False