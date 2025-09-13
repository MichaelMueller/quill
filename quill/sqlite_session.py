# builtin
from typing import Optional, Union, AsyncGenerator, TYPE_CHECKING, Callable, Awaitable
import os
# 3rd party
import pydantic
import aiosqlite
# local
from quill.session import Session, Select, WriteOperation
from quill.insert import Insert
from quill.update import Update
from quill.delete import Delete

class SqliteSession(Session):
    
    def __init__(self, create_connection:Callable[[], Awaitable[tuple[aiosqlite.Connection, bool]]]):
        super().__init__()
        self._create_connection = create_connection        
        self._connection:Optional[aiosqlite.Connection] = None
        self._transaction = False
        self._close_connection = False
        
    async def _assert_initialized(self):
        if self._connection == None:
            self._connection, self._close_connection = await self._create_connection()
        
    async def select(self, select:Select) -> AsyncGenerator[tuple | dict, None]:
        await self._assert_initialized()
        db = self._connection
        params = [] 
        sql = select.to_sql(dialect="sqlite", params=params)
        cursor = await db.execute(sql, params)
        column_names:list[str] = None
        if select.as_dict:
            column_names = [description[0] for description in cursor.description]
        async for row in cursor:
            yield row if column_names is None else dict(zip(column_names, row))       
                
    async def write(self, write_operation:WriteOperation) -> Optional[int]:
        await self._assert_initialized()
        db = self._connection
        if self._transaction is False:
            self._transaction = True
            await db.execute("BEGIN;")
        params = []
        sql = write_operation.to_sql(dialect="sqlite", params=params)
        cursor = await db.execute(sql, params)
        if isinstance(write_operation, Insert):
            return cursor.lastrowid
        elif isinstance(write_operation, (Update, Delete)):
            return cursor.rowcount
        else:
            return None
        
    async def commit(self) -> None:
        if self._connection != None and self._transaction:
            await self._connection.commit()

    async def rollback(self) -> None:
        if self._connection != None and self._transaction:
            await self._connection.rollback()

    async def close_session(self) -> None:
        if self._connection and self._close_connection:
            await self._connection.close()
            self._connection = None