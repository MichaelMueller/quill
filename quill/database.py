# builtin
from typing import Optional, Union, AsyncGenerator, Callable, Type, Awaitable, Literal
# 3rd party
import pydantic
# local
from quill.query import Query
from quill.select import Select
from quill.transaction import Transaction
from quill.write_operation import WriteOperation

HOOK_TYPE = Callable[[ Select | WriteOperation ], Awaitable[None]]
STATE_TYPE = Literal["pre_execute", "post_execute", "post_commit"] | None
HOOKABLE_TYPES = Type[Select] | Type[WriteOperation] | None

class Database:    
    def __init__(self):        
        self._hooks:dict[HOOK_TYPE, tuple[STATE_TYPE, HOOKABLE_TYPES, list[str]]] = {}

    def register_hook(self, 
                      hook:HOOK_TYPE,
                      state:STATE_TYPE=None, 
                      type_:HOOKABLE_TYPES=None, 
                      target_tables:list[str]=[]
                      ) -> None:
        if hook in self._hooks:
            raise ValueError("Hook already registered")
        self._hooks[hook] = (state, type_, target_tables)

    def unregister_hook(self, hook:HOOK_TYPE) -> None:
        del self._hooks[hook]
    
    async def execute_select(self, query:Select) -> AsyncGenerator[tuple, None]:
        for hook in self._find_hook("pre_execute", query, query.table_names):
            await hook(query)
            
        async for row in self._execute_select(query):
            yield row
            
        for hook in self._find_hook("post_execute", query, query.table_names):
            await hook(query)
    
    async def execute_transaction(self, query:Transaction) -> list[int]:
        for item in query.items:
            for hook in self._find_hook("pre_execute", item, [item.table_name]):
                await hook(item)
                
        inserted_id_or_affected_rows:list[int] = []    
        i = 0   
        async for result in self._execute_transaction(query):
            item = query.items[i]
            for hook in self._find_hook("post_execute", item, [item.table_name]):
                await hook(item)
            inserted_id_or_affected_rows.append(result)
            i += 1
            
        for item in query.items:
            for hook in self._find_hook("post_commit", item, [item.table_name]):
                await hook(item)
        return inserted_id_or_affected_rows
        
    async def _execute_select(self, query:Select) -> AsyncGenerator[tuple, None]:
        raise NotImplementedError()
        yield
    
    async def _execute_transaction(self, query:Transaction) -> AsyncGenerator[int, None]:
        raise NotImplementedError()
        yield
    
    def _find_hook(self, 
                   state:STATE_TYPE, 
                   type_:HOOKABLE_TYPES,
                   tables:list[str],
                   ) -> list[HOOK_TYPE]:
        matched_hooks: list[HOOK_TYPE] = []
        for hook, (hook_state, hook_type, hook_tables) in self._hooks.items():
            if hook_state != None and hook_state != state:
                continue
            if hook_type != None and hook_type != type_:
                continue
            if len(hook_tables) > 0 and not any( table in tables for table in hook_tables ):
                continue
            matched_hooks.append(hook)
        return matched_hooks