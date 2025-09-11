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
from quill.select import Select
from quill.comparison import Comparison
from quill.column_ref import ColumnRef

class Database:    
    def __init__(self):        
        self._modules:dict[Type["Module"], "Module"] = {}
        self._open_executes = 0

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

    async def by_id(self, table_name:str, id:int) -> Optional[tuple]:
        query = Select(table_name=table_name, where=Comparison(left=ColumnRef(name="id"), operator="=", right=id), limit=1)
        return await self.first(query)
    
    async def first(self, query:Select, first_col:bool=False) -> Optional[tuple]:
        async for row in self.execute(query):
            if first_col:
                return row[0]
            return row
        return None

    async def execute(self, query:Query, jwt:Optional[str]=None) -> AsyncGenerator[int | tuple, None]:
        
        if not isinstance(query, Query):
            raise ValueError(f"query must be an instance of Query, got {query}")

        # basic distinguish between Select and Transaction
        inserted_id_or_affected_rows: list[int] | None = None
        if not isinstance(query, Select):
            # caller can hand out single write operation for convenience -> wrap into transaction
            query = Transaction(items=[query]) if isinstance(query, WriteOperation) else query # shorthand
            if len(query.items) == 0:
                raise ValueError("Transaction must have at least one item")
            inserted_id_or_affected_rows = []

        affected_tables = query.table_names if isinstance(query, Select) else list( set( item.table_name for item in query.items ) )
        # filter modules by surveilled tables
        modules:list[Module] = []
        for m in self._modules.values():
            surveilled_tables = m.surveilled_tables()
            if surveilled_tables is None:
                continue
            if len(surveilled_tables) == 0 or any( t in affected_tables for t in surveilled_tables ):
                modules.append(m)
        modules = sorted(modules, key=lambda m: m.priority(), reverse=True)
        # notify modules sorted by priority
        if jwt != None:
            from quill.auth_module import AuthModule
            auth_module:AuthModule = self.module(AuthModule)
            if auth_module is not None:
                await auth_module.before_execute(query, jwt)
        for module in modules:
            await module.before_execute(query)

        # actually execute the query
        try:            
            if self._open_executes == 0:
                await self._open_session()
            self._open_executes += 1
                
            if inserted_id_or_affected_rows == None:  # Select
                async for row in self._execute_select(query):
                    yield row
            
                for module in modules:
                    await module.after_select(query)
            else:
                # make sure all operations are done before yielding any result
                current_op_idx = -1
                while current_op_idx + 1 < len(query.items): # query.items may change during iteration -> safe while loop!
                    current_op_idx += 1
                    write_op = query.items[current_op_idx]
                    # execute within the current transaction
                    result = await self._execute_write_operation(write_op)
                    inserted_id_or_affected_rows.append(result)                
                    for module in modules:
                        new_ops = await module.after_execute(query.items[current_op_idx], result)
                        if len(new_ops) > 0:
                            query.items.extend(new_ops)           
                
                await self._commit()
                for module in modules:
                    await module.after_commit(query, inserted_id_or_affected_rows)             
                
                # when all is done yield the results
                for result in inserted_id_or_affected_rows:
                    yield result
        finally:            
            self._open_executes -= 1
            if self._open_executes == 0:
                await self._close_session()
    
    async def _open_session(self) -> None:
        raise NotImplementedError()

    async def _execute_select(self, query:Select) -> AsyncGenerator[tuple, None]:
        # query items may change during iteration -> safe for loop!
        raise NotImplementedError()
        yield # make sure this is an async generator
    
    async def _execute_write_operation(self, write_operation:WriteOperation) -> int:
        raise NotImplementedError()
        
    async def _commit(self) -> None:
        raise NotImplementedError()

    async def _close_session(self) -> None:
        raise NotImplementedError()
    
    async def close(self) -> None:
        raise NotImplementedError()
