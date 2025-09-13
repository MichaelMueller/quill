# builtin
from typing import Optional, Union, AsyncGenerator, TYPE_CHECKING
import os
# 3rd party
import pydantic
import aiomysql
# local
from quill.session import Session, Select, WriteOperation
from quill.insert import Insert
from quill.update import Update
from quill.delete import Delete

class MysqlSession(Session):

    def __init__(self, pool:aiomysql.Pool):
        super().__init__()
        self._pool = pool
        self._connection:Optional[aiomysql.Connection] = None
        self._transaction:bool = False

    async def _assert_initialized(self):
        if self._connection is not None:
            return
        self._connection = await self._pool.acquire()
        return self

    async def select(self, select:Select) -> AsyncGenerator[tuple | dict, None]:
        await self._assert_initialized()
        params = []
        sql = select.to_sql(dialect="mysql", params=params)
        conn = self._connection
        async with conn.cursor() as cursor:
            await cursor.execute(sql, params)
            async for row in cursor:
                yield row if not select.as_dict else dict(zip([desc[0] for desc in cursor.description], row))

    async def write(self, write_operation:WriteOperation) -> Optional[int]:
        await self._assert_initialized()
        if self._transaction is False:
            self._transaction = True
        params = []
        sql = write_operation.to_sql(dialect="mysql", params=params)
        async with self._connection.cursor() as cursor:
            if isinstance(write_operation, Insert):
                await cursor.execute(sql, params)
                return cursor.lastrowid
            else:
                await cursor.execute(sql, params)
                if isinstance(write_operation, (Update, Delete)):
                    return cursor.rowcount
                else:
                    return None

    async def commit(self) -> None:
        if self._connection and self._transaction:
            await self._connection.commit()

    async def rollback(self) -> None:
        if self._connection and self._transaction:
            await self._connection.rollback()

    async def close_session(self) -> None:
        if self._connection:
            await self._pool.release(self._connection)
            self._connection = None