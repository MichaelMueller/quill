# builtin
from typing import Optional, Union, AsyncGenerator
import os
# 3rd party
import pydantic
import aiosqlite
# local
from quill.database import Database, Query, Select, Transaction, WriteOperation
from quill.insert import Insert

class SqliteDatabase(Database):
    
    def __init__(self, db_path:Optional[str]=":memory:"):
        super().__init__()
        self._db_path = db_path
        # state
        self._db = None
        self._in_memory_or_unknown_tmp_file:Optional[bool] = None
            
    async def _open_session(self) -> None:
        if self._in_memory_or_unknown_tmp_file is None:
            self._in_memory_or_unknown_tmp_file = self._db_path == ":memory:" or self._db_path == ""
            if not self._in_memory_or_unknown_tmp_file:
                db_dir = os.path.dirname(self._db_path)
                os.makedirs(db_dir, exist_ok=True)
        if self._db is None:
            self._db = await aiosqlite.connect(self._db_path)

    async def _execute_select(self, query:Select) -> AsyncGenerator[tuple, None]:
        db = self._db
        sql, params = query.to_sql()
        async with db.execute(sql, params) as cursor:
            async for row in cursor:        # row is a tuple, e.g. (1, "Alice", 31)
                yield row        
        
    async def _execute_write_operation(self, write_operation:WriteOperation) -> int:
        db = self._db
        
        sql, params = write_operation.to_sql()
        async with db.execute(sql, params) as cursor:
            if isinstance(write_operation, Insert):
                return cursor.lastrowid
            else:
                return cursor.rowcount
    
    async def _commit(self) -> None:
        await self._db.commit()

    async def _close_session(self) -> None:
        if self._in_memory_or_unknown_tmp_file == False:
            await self.close()

    async def close(self) -> None:
        if self._db != None:
            await self._db.close()
            self._db = None