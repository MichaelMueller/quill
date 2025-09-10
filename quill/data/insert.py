# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.data.write_operation import WriteOperation

class Insert(WriteOperation):
    type:Literal["insert"] = "insert"
    table_name: str
    values: dict[str, Optional[Any]]