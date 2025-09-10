# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.data.write_operation import WriteOperation

class Update(WriteOperation):
    type:Literal["update"] = "update"    
    table_name: str
    values: dict[str, Optional[Any]]
    id:int
    