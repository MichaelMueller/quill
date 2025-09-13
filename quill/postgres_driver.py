# builtin
from multiprocessing import pool
from typing import Optional, Union, AsyncGenerator
import os
# 3rd party
import pydantic
import asyncpg
# local
from quill.postgres_session import PostgresSession
from quill.driver import Driver, Session
from quill.insert import Insert
from quill.postgres_driver_params import PostgresDriverParams

class PostgresDriver(Driver):
    
    def __init__(self, params:PostgresDriverParams):
        super().__init__()
        self._params = params
        # state
        self._pool:Optional[asyncpg.Pool] = None
                    
    async def create_session(self) -> Session:     
        
        # new connection for real file-based db, shared connection for in-memory or unknown temp file db
        if self._pool is None:
            params = self._params
            self._pool = await asyncpg.create_pool(
                user=params.user,
                password=params.password,
                database=params.database,
                host=params.host,
                port=params.port,
                min_size=params.pool_min_size,
                max_size=params.pool_max_size,
            )
        return PostgresSession(self._pool, self._params.timeout)

    async def close(self) -> None:
        if self._pool != None:
            await self._pool.close()
            self._pool = None