# builtin
from typing import Any
# 3rd party
import pydantic
# local

IDENTIFIER_REGEX = r"^[A-Za-z_][A-Za-z0-9_]*$"

class SqlExpression(pydantic.BaseModel):
    type:str
    
    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        raise NotImplementedError()