# builtin
from typing import Optional, Union, AsyncGenerator, Callable, Type, Any, Literal, TYPE_CHECKING
# 3rd party
# local
if TYPE_CHECKING:
    from quill.module import Module
from quill.query import Query
from quill.select import Select
from quill.transaction import Transaction
from quill.write_operation import WriteOperation
from quill.select import Select
from quill.comparison import Comparison
from quill.ref import Ref
from quill.driver import Driver
from quill.database_params import DatabaseParams

class Database:    
    def __init__(self, db_params: Optional[DatabaseParams] = None):        
        self._db_params = db_params or DatabaseParams()
        self._modules:dict[Type["Module"], "Module"] = {}
        self._driver: Optional[Driver] = None

    async def register_module(self, module_type:Type["Module"], args:Optional[dict[str, Any]]=None, exists_ok:bool = False) -> None:
        if module_type in self._modules:
            if exists_ok:
                return
            raise ValueError("Module already registered")
        module = module_type(self) if args is None else module_type(self, **args)
        await module.initialize()
        self._modules[module_type] = module

    def module(self, module_type:Type["Module"]) -> Optional["Module"]:
        return self._modules.get(module_type, None)

    async def unregister_module(self, module_type:Type["Module"]) -> None:
        module = self._modules[module_type] 
        await module.shutdown()
        del self._modules[module_type]    

    async def first_row(self, table_name:str) -> Optional[tuple]:
        query = Select(table_names=[table_name], limit=1)
        return await self.one(query)
    
    async def by_id(self, table_name:str, id:int) -> Optional[tuple]:
        query = Select(table_names=[table_name], where=Comparison(left=Ref(name="id"), operator="=", right=id), limit=1)
        return await self.one(query)

    async def one(self, query:Select, first_col:bool=False) -> Optional[tuple]:
        async for row in self.execute(query):
            if first_col:
                return row[0]
            return row
        return None
    
    async def driver(self) -> Driver:
        if self._driver is None:
            if self._db_params.driver == "sqlite":
                from quill.sqlite_driver import SqliteDriver
                self._driver = SqliteDriver(db_path=self._db_params.db_url)
            else:
                raise ValueError(f"Unsupported driver: {self._db_params.driver}")
        return self._driver

    async def execute(self, query:Query) -> AsyncGenerator[int | tuple | dict, None]:
        
        if not isinstance(query, Query):
            raise ValueError(f"query must be an instance of Query, got {query}")

        # basic distinguish between Select and Transaction
        inserted_ids_and_affected_rows: list[int] | None = None
        if not isinstance(query, Select):
            # caller can hand out single write operation for convenience -> wrap into transaction
            query = Transaction(items=[query]) if isinstance(query, WriteOperation) else query # shorthand
            if len(query.items) == 0:
                raise ValueError("Transaction must have at least one item")
            inserted_ids_and_affected_rows = []

        # sort modules by priority
        modules:list[Module] = []
        modules = sorted(modules, key=lambda m: m.priority(), reverse=True)

        # open db session
        driver = await self.driver()
        db_session = await driver.create_session()
        async with db_session:
            # Select
            if inserted_ids_and_affected_rows == None:  
                for module in modules:
                    await module.pre_select(query, db_session)
                async for row in db_session.select(query):
                    for module in modules:
                        await module.post_select(query, db_session, row)
                    yield row
            # Transaction
            else:                
                for op in query.items:
                    for module in modules:
                        await module.pre_execute(op, db_session)
                        
                    result = await db_session.write(op)
                    inserted_ids_and_affected_rows.append(result)
                    
                    for module in modules:
                        await module.post_execute(op, db_session, result)
        
        # yield results after session is closed and committed
        if inserted_ids_and_affected_rows is not None:
            for result in inserted_ids_and_affected_rows:
                yield result

    async def close(self) -> None:
        if self._driver is not None:
            await self._driver.close()
            self._driver = None