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
    
    async def __aenter__(self):
        raise NotImplementedError()

    async def select(self, select:Select) -> AsyncGenerator[tuple | dict, None]:
        # query items may change during iteration -> safe for loop!
        raise NotImplementedError()
        yield # make sure this is an async generator
    
    async def write(self, write_operation:WriteOperation) -> Optional[int]:
        raise NotImplementedError()
        
    async def _commit(self) -> None:
        raise NotImplementedError()

    async def _close_session(self) -> None:
        raise NotImplementedError()    

    async def __aexit__(self, exc_type, exc, tb):
        await self._commit()
        await self._close_session()