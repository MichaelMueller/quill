# builtin
from typing import Optional, Union, AsyncGenerator, Callable, Type, Awaitable, Union, TYPE_CHECKING
# 3rd party
import pydantic
# local
if TYPE_CHECKING:
    from quill.database import Database
from quill.select import Select
from quill.transaction import Transaction
from quill.write_operation import WriteOperation

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
    
    async def before_execute(self, query:Union[Select, Transaction]) -> None:
        pass
    
    async def after_execute(self, write_operation:WriteOperation, inserted_id_or_affected_rows:Optional[int]=None) -> list[WriteOperation]:
        return []

    async def after_select(self, query:Select) -> None:
        pass
    
    async def after_commit(self, query:Union[Select, Transaction], inserted_id_or_affected_rows:list[int]|None) -> None:
        pass
    
    def priority(self) -> int:
        return 0