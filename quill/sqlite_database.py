# builtin
from typing import Optional, Union, AsyncGenerator
# 3rd party
import pydantic
# local
from quill.database import Database, Query, Select, Transaction

class SqliteDatabase(Database):
    
    def __init__(self, db_path:Optional[str]=":memory:"):
        super().__init__()
        self._db_path = db_path

    async def _execute_select(self, query:Select) -> AsyncGenerator[int, None]:
        raise NotImplementedError()
    
    async def _execute_transaction(self, query:Transaction) -> list[int]:
        raise NotImplementedError()
    