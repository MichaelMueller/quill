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
from quill.session import Session

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
            
    async def pre_select(self, select:Select, db_session:Session) -> None:
        pass
    
    async def post_select(self, select:Select, db_session:Session, row:Union[tuple, dict]) -> None:
        pass    
        
    async def pre_execute(self, op:WriteOperation, db_session:Session) -> None:
        pass
        
    async def post_execute(self, op:WriteOperation, db_session:Session, inserted_id_or_affected_rows:Optional[int]=None) -> None:
        pass
    
    async def post_commit(self, transaction:Optional[Transaction]) -> None:
        pass
    
    def priority(self) -> int:
        return 0