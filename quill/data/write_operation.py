# builtin
from typing import Literal
# 3rd party
import pydantic
# local

class WriteOperation(pydantic.BaseModel):
    type:Literal["create_table", "insert", "update", "delete"]