# builtin
from typing import Optional, Union, AsyncGenerator, Callable, Type, Awaitable, Union, TYPE_CHECKING
import sys
# 3rd party
import pydantic
# local
if TYPE_CHECKING:
    from quill.database import Database
    from quill.user import User
    from quill.query import Query
from quill.module import Module

class AuthModule(Module):    
    
    def __init__(self, db: "Database"):        
        super().__init__(db)    
        
    def priority(self) -> int:
        return sys.maxsize
    
    async def get_current_user(self, query:"Query") -> Optional[User]:
        raise NotImplementedError()