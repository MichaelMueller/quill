# builtin
from typing import Any, Literal, Optional
# 3rd party
import pydantic
# local

class User(pydantic.BaseModel):
    id: int
    username: str
    email: Optional[str]
    is_admin: bool = False