# builtin
from typing import Optional, Union, AsyncGenerator, TYPE_CHECKING
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
    
    def __init__(self, connection:aiosqlite.Connection, close_on_exit:bool=True):
        super().__init__()
        self._connection = connection
        self._close_on_exit = close_on_exit
            
    async def __aenter__(self):
        if not self._connection:
            raise RuntimeError("Session was closed")
        return self

    async def select(self, select:Select) -> AsyncGenerator[tuple | dict, None]:
        db = self._connection
        sql, params = select.to_sqlite_sql()
        async with db.execute(sql, params) as cursor:
            column_names:list[str] = None
            if select.as_dict:
                column_names = [description[0] for description in cursor.description]
            async for row in cursor:
                yield row if column_names is None else dict(zip(column_names, row))       
                
    async def write(self, write_operation:WriteOperation) -> Optional[int]:
        db = self._connection
        
        sql, params = write_operation.to_sqlite_sql()
        async with db.execute(sql, params) as cursor:
            if isinstance(write_operation, Insert):
                return cursor.lastrowid
            elif isinstance(write_operation, (Update, Delete)):
                return cursor.rowcount
            else:
                return None
        
    async def _commit(self) -> None:
        await self._connection.commit()

    async def _close_session(self) -> None:
        if self._close_on_exit:
            await self._connection.close()
        self._connection = None