# builtin
from typing import Optional, Union, AsyncGenerator
# 3rd party
import pydantic
# local
from quill.query import Query
from quill.select import Select
from quill.transaction import Transaction

class Database:    
    
    async def execute(self, query:Query) -> Union[ list[int], AsyncGenerator[int, None], None ]:
        if query.type == "select":
            return await self.execute_select(query)
        elif query.type == "transaction":
            return await self.execute_transaction(query)
        else:
            raise ValueError(f"Unsupported query type: {query}")

    async def execute_select(self, query:Select) -> AsyncGenerator[int, None]:
        raise NotImplementedError()
    
    async def execute_transaction(self, query:Transaction) -> list[int]:
        raise NotImplementedError()