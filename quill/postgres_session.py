# builtin
from typing import Optional, Union, AsyncGenerator, TYPE_CHECKING
import os
# 3rd party
import pydantic
import asyncpg
# local
from quill.session import Session, Select, WriteOperation
from quill.insert import Insert
from quill.update import Update
from quill.delete import Delete

class PostgresSession(Session):
    
    def __init__(self, pool:asyncpg.Pool, timeout:float):
        super().__init__()
        self._pool = pool
        self._timeout = timeout
        self._connection:Optional[asyncpg.Connection] = None
            
    async def __aenter__(self):
        if not self._pool:
            raise RuntimeError("Session was closed")
        self._connection = await self._pool.acquire(timeout=self._timeout)
        return self

    async def select(self, select:Select) -> AsyncGenerator[tuple | dict, None]:
        sql, params = select.to_sql(dialect="postgres")
        conn = self._connection
        async with conn.transaction():
            async for record in conn.cursor(sql, *params):
                yield record if not select.as_dict else dict(record) 
                
    async def write(self, write_operation:WriteOperation) -> Optional[int]:
        sql, params = write_operation.to_sql(dialect="postgres")        
        if isinstance(write_operation, Insert):
            sql += " RETURNING id"
            row = await self._connection.fetchrow(sql, params)
            return row["id"]
        else:            
            result = await self._connection.execute(sql, params)
            if isinstance(write_operation, (Update, Delete)):
                _, rows = result.split()
                return int(rows)
            else:
                return None
        
    async def _commit(self) -> None:
        await self._connection.commit()

    async def _close_session(self) -> None:
        await self._pool.release(self._connection, timeout=self._timeout)
        self._connection = None
        self._pool = None