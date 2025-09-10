# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.write_operation import WriteOperation
from quill.column import Column

class ManageIndex(WriteOperation):
    type:Literal["create_index", "drop_index"]
    table_name: str
    columns: list[str]
    unique: bool = False
    
    def _index_name(self) -> str:
        return f"{self.table_name}_{'_'.join(self.columns)}" + ("_idx" if not self.unique else "_uidx")
    