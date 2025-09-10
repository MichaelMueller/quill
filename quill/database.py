# builtin
from typing import Optional, Union, AsyncGenerator, Callable, Type, Awaitable, Literal, TYPE_CHECKING
# 3rd party
import pydantic
# local
if TYPE_CHECKING:
    from quill.hook import Hook
from quill.query import Query
from quill.select import Select
from quill.transaction import Transaction
from quill.write_operation import WriteOperation

class Database:    
    def __init__(self):        
        self._hooks:set["Hook"] = set()

    def register_hook(self, hook:"Hook") -> None:
        if hook in self._hooks:
            raise ValueError("Hook already registered")
        self._hooks.add(hook)

    def unregister_hook(self, hook:"Hook") -> None:
        self._hooks.remove(hook)

    async def execute(self, query:Query) -> AsyncGenerator[int | tuple, None]:
        if not isinstance(query, Query):
            raise ValueError(f"query must be an instance of Query, got {query}")
        
        for hook in self._hooks:
            await hook(self, query, before_execute=True)

        if isinstance(query, Select):
            async for row in self._execute_select(query):
                yield row
        else:
            if isinstance(query, WriteOperation):
                transaction = Transaction(items=[query])
            else:
                transaction = query 
            inserted_id_or_affected_rows: list[int] = []
            # make sure all operations are done before yielding any result
            async for result in self._execute_transaction(transaction):
                inserted_id_or_affected_rows.append(result)
                
            for result in inserted_id_or_affected_rows:
                yield result
        
        for hook in self._hooks:
            await hook(self, query, before_execute=False)

    async def _execute_select(self, query:Select) -> AsyncGenerator[tuple, None]:
        raise NotImplementedError()
        yield
    
    async def _execute_transaction(self, query:Transaction) -> AsyncGenerator[int, None]:
        raise NotImplementedError()
        yield
    