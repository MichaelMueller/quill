# builtin
from typing import Any, Literal
# 3rd party
import pydantic
# local

IDENTIFIER_REGEX = r"^[A-Za-z_][A-Za-z0-9_]*$"
SUPPORTED_DIALECTS = Literal["sqlite", "postgres", "mysql"]

class SqlExpression(pydantic.BaseModel):
    type:str

    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite", params:list[Any]=[]) -> str:
        raise NotImplementedError()
        
    def next_placeholder(self, dialect:SUPPORTED_DIALECTS="sqlite", params:list[Any]=[]) -> str:
        if dialect == "mysql":
            return "%s"
        elif dialect == "postgres":
            return f"${len(params)+1}"
        else: # sqlite
            return "?"