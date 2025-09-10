# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.data.write_operation import WriteOperation
from quill.data.column import Column

class Expression:
    
    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        raise NotImplementedError()