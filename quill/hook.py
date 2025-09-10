# builtin
from typing import Optional, Union, AsyncGenerator, Callable, Type, Awaitable, Literal, TYPE_CHECKING
# 3rd party
import pydantic
# local
if TYPE_CHECKING:
    from quill.database import Database
    from quill.query import Query

class Hook:    
    async def __call__(self, db: "Database", query:"Query", before_execute:bool) -> None:
        raise NotImplementedError()