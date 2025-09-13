# builtin
from typing import Optional, Union, AsyncGenerator
import os, asyncio
# 3rd party
import pydantic
import aiomysql
# local
from quill.mysql_session import MysqlSession
from quill.driver import Driver, Session
from quill.insert import Insert
from quill.mysql_driver_params import MysqlDriverParams

class MysqlDriver(Driver):

    def __init__(self, params: MysqlDriverParams):
        super().__init__()
        self._params = params
        # state
        self._pool: Optional[aiomysql.Pool] = None

    async def create_session(self) -> Session:
        if self._pool is None:
            params = self._params
            loop = asyncio.get_running_loop()
            self._pool = await aiomysql.create_pool(
                user=params.user,
                password=params.password,
                db=params.database,
                host=params.host,
                port=params.port,
                minsize=params.pool_min_size,
                maxsize=params.pool_max_size,
                loop=loop
            )
        return MysqlSession(self._pool)

    async def close(self) -> None:
        if self._pool is not None:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None
