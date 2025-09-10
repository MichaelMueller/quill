# builtin
from typing import Optional, Union, AsyncGenerator, Callable
# 3rd party
import pydantic
# local
from quill.query import Query
from quill.select import Select
from quill.transaction import Transaction

class Database:    
    def __init__(self):        
        pass
    
    async def execute_select(self, query:Select) -> AsyncGenerator[int, None]:
        async for row in self._execute_select(query):
            yield row
    
    async def execute_transaction(self, query:Transaction) -> list[int]:
        return await self._execute_transaction(query)
        
    async def _execute_select(self, query:Select) -> AsyncGenerator[int, None]:
        raise NotImplementedError()
        yield
    
    async def _execute_transaction(self, query:Transaction) -> list[int]:
        raise NotImplementedError()
    