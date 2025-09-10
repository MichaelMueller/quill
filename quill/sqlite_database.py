# builtin
from typing import Optional, Union, AsyncGenerator
import os
# 3rd party
import pydantic
import aiosqlite
# local
from quill.database import Database, Query, Select, Transaction

class SqliteDatabase(Database):
    
    def __init__(self, db_path:Optional[str]=":memory:"):
        super().__init__()
        self._db_path = db_path
        # state
        self._db_path_asserted: bool = False
        self._db = None

    async def execute_select(self, query:Select) -> AsyncGenerator[int, None]:
        await self._assert_db()
        try:
            db = self._db if self._db != None else await aiosqlite.connect(self._db_path)            
            sql, params = query.to_sqlite_sql()
            async with db.execute(sql, params) as cursor:
                async for row in cursor:        # row is a tuple, e.g. (1, "Alice", 31)
                    yield list(row)             # convert to list: [1, "Alice", 31]
        finally:
            if self._db == None:
                await db.close()
    
    async def execute_transaction(self, query:Transaction) -> list[int]:
        inserted_id_or_affected_rows:list[int] = []
        await self._assert_db()
        try:
            db = self._db if self._db != None else await aiosqlite.connect(self._db_path)     
            for operation in query.items:
                sql, params = operation.to_sqlite_sql()
                async with db.execute(sql, params) as cursor:
                    if operation.type == "insert":
                        inserted_id_or_affected_rows.append(await cursor.lastrowid)
                    else:
                        inserted_id_or_affected_rows.append(await cursor.rowcount)
            await db.commit()        
        finally:
            if self._db == None:
                await db.close()
        return inserted_id_or_affected_rows
    
    async def _assert_db(self) -> None:
        if not self._db_path_asserted:
            if "/" in self._db_path or "\\" in self._db_path:
                db_dir = os.path.dirname(self._db_path)
                os.makedirs(db_dir, exist_ok=True)
            elif self._db_path == ":memory:":
                self._db = await aiosqlite.connect(self._db_path)
            self._db_path_asserted = True
