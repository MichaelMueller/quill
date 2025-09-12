# builtin
from typing import Any, Literal
# 3rd party
import pydantic
# local

IDENTIFIER_REGEX = r"^[A-Za-z_][A-Za-z0-9_]*$"
SUPPORTED_DIALECTS = Literal["sqlite", "postgres"]

class SqlExpression(pydantic.BaseModel):
    type:str

    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite") -> tuple[str, list[Any]]:
        raise NotImplementedError()
        