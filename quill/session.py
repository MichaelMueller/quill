# builtin
from typing import Optional, Union, AsyncGenerator, Callable, Type, Awaitable, Literal, TYPE_CHECKING
# 3rd party
import pydantic
# local
from quill.select import Select
from quill.write_operation import WriteOperation

class Session:
    def __init__(self):
        pass
    
    async def select(self, select:Select) -> AsyncGenerator[tuple | dict, None]:
        # query items may change during iteration -> safe for loop!
        raise NotImplementedError()
        yield # make sure this is an async generator
    
    async def write(self, write_operation:WriteOperation) -> Optional[int]:
        raise NotImplementedError()
        
    async def commit(self) -> None:
        raise NotImplementedError()
    
    async def rollback(self) -> None:
        pass

    async def close_session(self) -> None:
        raise NotImplementedError()    
