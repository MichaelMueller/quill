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
        self._initialized: bool = False
    
    def db(self) -> "Database":
        return self._db
    
    async def initialize(self) -> None:
        if not self._initialized:
            await self._initialize()
        self._initialized = True
        
    async def _initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass    
    
    async def on_query(self, query:"Query", before_execute:bool) -> None:
        pass