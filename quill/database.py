# builtin
from typing import Optional, Union, AsyncGenerator, Callable, Type, Awaitable, Literal, TYPE_CHECKING
# 3rd party
import pydantic
# local
if TYPE_CHECKING:
    from quill.module import Module
from quill.query import Query
from quill.select import Select
from quill.transaction import Transaction
from quill.write_operation import WriteOperation

class Database:    
    def __init__(self):        
        self._modules:dict[Type["Module"], "Module"] = {}

    async def register_module(self, module_type:Type["Module"], exists_ok:bool = False) -> None:
        if module_type in self._modules:
            if exists_ok:
                return
            raise ValueError("Module already registered")
        module = module_type(self)
        await module.initialize()
        self._modules[module_type] = module

    def module(self, module_type:Type["Module"]) -> Optional["Module"]:
        return self._modules.get(module_type, None)

    async def unregister_module(self, module_type:Type["Module"]) -> None:
        module = self._modules[module_type] 
        await module.shutdown()
        del self._modules[module_type]    

    async def execute(self, query:Query) -> AsyncGenerator[int | tuple, None]:
        if not isinstance(query, Query):
            raise ValueError(f"query must be an instance of Query, got {query}")

        # basic distinguish between Select and Transaction
        inserted_id_or_affected_rows: list[int] | None = None
        if not isinstance(query, Select):
            # caller can hand out single write operation for convenience -> wrap into transaction
            query = Transaction(items=[query]) if isinstance(query, WriteOperation) else query # shorthand
            inserted_id_or_affected_rows = []

        # notify modules sorted by priority
        modules = sorted(self._modules.values(), key=lambda m: m.priority(), reverse=True)
        for module in modules:
            await module.before_execute(query)

        # actually run the query
        if inserted_id_or_affected_rows == None:  # Select
            async for row in self._execute_select(query):
                yield row
        else:
            # make sure all operations are done before yielding any result
            async for result in self._execute_transaction(query):
                inserted_id_or_affected_rows.append(result)
                
            for result in inserted_id_or_affected_rows:
                yield result
            
        for module in modules:
            await module.after_execute(query, inserted_id_or_affected_rows)

    async def _execute_select(self, query:Select) -> AsyncGenerator[tuple, None]:
        raise NotImplementedError()
        yield # make sure this is an async generator
    
    async def _execute_transaction(self, query:Transaction) -> AsyncGenerator[int, None]:
        raise NotImplementedError()
        yield # make sure this is an async generator
