# builtin
from typing import Optional, Union, AsyncGenerator
# 3rd party
import pydantic
# local
from quill.query import Query
from quill.select import Select
from quill.transaction import Transaction

class Database:    
    
    async def execute_select(self, query:Select) -> AsyncGenerator[int, None]:
        raise NotImplementedError()
    
    async def execute_transaction(self, query:Transaction) -> list[int]:
        raise NotImplementedError()