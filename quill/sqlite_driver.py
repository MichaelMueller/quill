# builtin
from typing import Optional, Union, AsyncGenerator
import os
# 3rd party
import pydantic
import aiosqlite
# local
from quill.sqlite_session import SqliteSession
from quill.driver import Driver, Session
from quill.insert import Insert
from quill.sqlite_driver_params import SqliteDriverParams

class SqliteDriver(Driver):
    
    def __init__(self, params:SqliteDriverParams):
        super().__init__()
        self._params = params
        # state
        self._db:Optional[aiosqlite.Connection] = None
        self._in_memory_or_unknown_tmp_file:Optional[bool] = None
                    
    async def create_session(self) -> Session:     
        
        # new connection for real file-based db, shared connection for in-memory or unknown temp file db
        if self._in_memory_or_unknown_tmp_file is None:

            self._in_memory_or_unknown_tmp_file = self._params.database_file == ":memory:" or self._params.database_file == ""

            if self._in_memory_or_unknown_tmp_file:
                self._db = await self._new_connection()
            else:
                db_dir = os.path.dirname(self._params.database_file)
                os.makedirs(db_dir, exist_ok=True)
           
        db = self._db if self._in_memory_or_unknown_tmp_file else await self._new_connection()
        return SqliteSession( db, close_on_exit = self._in_memory_or_unknown_tmp_file == False )
    
    async def _new_connection(self) -> aiosqlite.Connection:
        db = await aiosqlite.connect(self._params.database_file, timeout=self._params.timeout)
        if self._params.wal_mode:
            await db.execute("PRAGMA journal_mode=WAL;")
        return db
    
    async def close(self) -> None:
        if self._db != None:
            await self._db.close()
            self._db = None