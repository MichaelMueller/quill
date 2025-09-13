# builtin
from typing import Optional, Union, AsyncGenerator, TYPE_CHECKING
import os
# 3rd party
import pydantic
import asyncpg
from asyncpg.transaction import Transaction as PgTransaction
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
        self._transaction:Optional[PgTransaction] = None
            
    async def _assert_initialized(self):
        if self._connection != None:
            return
        self._connection = await self._pool.acquire(timeout=self._timeout)
        return self

    async def select(self, select:Select) -> AsyncGenerator[tuple | dict, None]:
        await self._assert_initialized()
        params = []
        sql = select.to_sql(dialect="postgres", params=params)
        conn = self._connection
        async with conn.transaction():
            async for record in conn.cursor(sql, *params):
                yield record if not select.as_dict else dict(record) 
                
    async def write(self, write_operation:WriteOperation) -> Optional[int]:
        await self._assert_initialized()
        if self._transaction is None:
            self._transaction = self._connection.transaction()
            await self._transaction.start()
        params = []
        sql = write_operation.to_sql(dialect="postgres", params=params)
        if isinstance(write_operation, Insert):
            sql += " RETURNING id"
            row = await self._connection.fetchrow(sql, *params)
            return row["id"]
        else:            
            result = await self._connection.execute(sql, *params)
            if isinstance(write_operation, (Update, Delete)):
                _, rows = result.split()
                return int(rows)
            else:
                return None
        
    async def commit(self) -> None:
        if self._transaction:
            await self._transaction.commit()
        
    async def rollback(self) -> None:
        if self._transaction:
            await self._transaction.rollback()

    async def close_session(self) -> None:
        if self._connection:
            await self._pool.release(self._connection, timeout=self._timeout)
            self._connection = None