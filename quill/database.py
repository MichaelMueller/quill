# builtin
from typing import Optional, Union, AsyncGenerator, Callable, Type, Any, Literal, TYPE_CHECKING
# 3rd party
# local
if TYPE_CHECKING:
    from quill.module import Module
    from quill.session import Session
from quill.sql_query import SqlQuery
from quill.select import Select
from quill.transaction import Transaction
from quill.write_operation import WriteOperation
from quill.select import Select
from quill.comparison import Comparison
from quill.ref import Ref
from quill.driver import Driver
from quill.database_params import DatabaseParams, SqliteDriverParams, PostgresDriverParams, MysqlDriverParams

class Database:    
    def __init__(self, db_params: Optional[DatabaseParams] = None):        
        self._db_params = db_params or DatabaseParams()
        self._modules:dict[Type["Module"], "Module"] = {}
        self._driver: Optional[Driver] = None
        self._session:Optional["Session"] = None        

    async def register_module(self, module_type:Type["Module"], args:Optional[dict[str, Any]]=None, exists_ok:bool = False) -> None:
        mros = self._module_mros(module_type)
        
        if not exists_ok:
            for mro in mros:
                if mro in self._modules:
                    raise ValueError(f"Cannot register module {module_type.__name__}, because base class {mro.__name__} is already registered")

        module = module_type(self) if args is None else module_type(self, **args)
        await module.initialize()
        for mro in mros:
            self._modules[mro] = module

    def module(self, module_type:Type["Module"]) -> Optional["Module"]:
        return self._modules.get(module_type, None)

    async def unregister_module(self, module_type:Type["Module"]) -> None:
        module = self._modules[module_type] 
        await module.shutdown()
        mros = self._module_mros(module_type)
        for mro in mros:
            del self._modules[mro]

    def _module_mros(self,module_type:Type["Module"]) -> set[Type["Module"]]:
        from quill.module import Module        
        mros = set( module_type.mro() )
        mros.remove(object)
        mros.remove(Module)
        return mros
    
    async def first_row(self, table_name:str) -> Optional[tuple]:
        query = Select(table_names=[table_name], limit=1, offset=0, order_by=[("id","asc")])
        return await self.one(query)
    
    async def by_id(self, table_name:str, id:int) -> Optional[tuple]:
        query = Select(table_names=[table_name], where=Comparison(left=Ref(name="id"), operator="=", right=id), limit=1)
        return await self.one(query)

    async def one(self, query:Select, first_col:bool=False) -> Union[ dict, tuple, int, str, float, bool, None]:
        row: Optional[Union[tuple, dict]] = None
        async for curr_row in self.execute(query):
            if row is None:
                row = curr_row
        if row is not None and first_col:
            return row[0] if isinstance(row, tuple) else next(iter(row.values()))
        return row
    
    async def driver(self) -> Driver:
        if self._driver is None:
            if isinstance(self._db_params.driver, PostgresDriverParams):                
                from quill.postgres_driver import PostgresDriver
                self._driver = PostgresDriver(self._db_params.driver)
            elif isinstance(self._db_params.driver, MysqlDriverParams):
                from quill.mysql_driver import MysqlDriver
                self._driver = MysqlDriver(self._db_params.driver)
            elif isinstance(self._db_params.driver, SqliteDriverParams):
                from quill.sqlite_driver import SqliteDriver
                self._driver = SqliteDriver(self._db_params.driver)
            else:
                raise ValueError(f"Unsupported driver: {self._db_params.driver}")
        return self._driver

    async def execute(self, query:SqlQuery) -> AsyncGenerator[int | tuple | dict, None]:
        
        if not isinstance(query, SqlQuery):
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
        modules:list[Module] = list( set( self._modules.values() ) )
        modules = sorted(modules, key=lambda m: m.priority(), reverse=True)

        # open db session
        try:
            session_created = False
            if self._session is None:
                driver = await self.driver()
                self._session = await driver.create_session()
                session_created = True
            db_session = self._session
            
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
                        
                await db_session.commit()
                
                # yield results after session is closed and committed
                if inserted_ids_and_affected_rows is not None:
                    for module in modules:
                        await module.post_commit(query)
                        
                    for result in inserted_ids_and_affected_rows:
                        yield result
                    
        except Exception as e:
            if session_created:
                await self._session.rollback()
            raise e
        finally:
            if session_created:
                await self._session.close_session()
                self._session = None

    async def close(self) -> None:
        if self._driver is not None:
            await self._driver.close()
            self._driver = None