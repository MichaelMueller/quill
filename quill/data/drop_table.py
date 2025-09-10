# builtin
from typing import Optional, Literal
# 3rd party
import pydantic
# local
from quill.data.write_operation import WriteOperation
from quill.data.column import Column

class DropTable(WriteOperation):
    type:Literal["drop_table"] = "drop_table"
    table_name: str