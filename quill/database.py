# builtin
from typing import Optional, Union, AsyncGenerator
# 3rd party
import pydantic
# local
from quill.data.query import Query
from quill.data.select import Select
from quill.data.transaction import Transaction

class Database:    
    
    async def execute(self, query:Query) -> Union[ list[int], AsyncGenerator[int, None], None ]:
        if query.type == "select":
            return await self._execute_select(query)
        elif query.type == "transaction":
            return await self._execute_transaction(query)

    async def _execute_select(self, query:Select) -> AsyncGenerator[int, None]:
        raise NotImplementedError()
    
    async def _execute_transaction(self, query:Transaction) -> list[int]:
        raise NotImplementedError()