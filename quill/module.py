# builtin
from typing import Optional, Union, AsyncGenerator, Callable, Type, Awaitable, Literal, TYPE_CHECKING
# 3rd party
import pydantic
# local
if TYPE_CHECKING:
    from quill.database import Database
    from quill.query import Query

class Module:    
    
    def __init__(self, db: "Database"):
        self._db = db
    
    async def initialize(self) -> None:
        pass
    
    async def shutdown(self) -> None:
        pass    
    
    async def on_query(self, query:"Query", before_execute:bool) -> None:
        pass