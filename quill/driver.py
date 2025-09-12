# builtin
from typing import Optional, Union, AsyncGenerator, Callable, Type, Awaitable, Literal, TYPE_CHECKING
# 3rd party
import pydantic
# local    
from quill.sql_expression import SqlExpression
from quill.session import Session

class Driver:
    async def create_session(self) -> Session:
        raise NotImplementedError()
    
    async def close(self) -> None:
        raise NotImplementedError()