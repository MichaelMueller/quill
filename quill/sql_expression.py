# builtin
from typing import Any
# 3rd party
import pydantic
# local

class SqlExpression(pydantic.BaseModel):
    type:str
    
    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        raise NotImplementedError()