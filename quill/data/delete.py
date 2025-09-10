# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.data.write_operation import WriteOperation

class Delete(WriteOperation):
    type:Literal["delete"] = "delete"    
    table_name: str
    ids: list[int]