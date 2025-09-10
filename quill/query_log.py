# builtin
from typing import Optional, Union, AsyncGenerator, TYPE_CHECKING
import os, datetime
# 3rd party
import pydantic
import aiosqlite
# local
from quill.module import Module
from quill.column import Column
from quill.create_table import CreateTable
from quill.insert import Insert
from quill.write_operation import WriteOperation
from quill.transaction import Transaction
if TYPE_CHECKING:
    from quill.database import Database
    from quill.query import Query

class QueryLog(Module):

    def __init__(self, db: "Database"):
        super().__init__(db)
        self._table_initialized: bool = False

    async def on_query(self, query:"Query", before_execute:bool) -> None:
        if isinstance(query, WriteOperation) and query.table_name == "query_logs":
            return        
        
        if self._table_initialized == False:
            await self._initialize_table()
            self._table_initialized = True
        
        if before_execute == False:
            async for _ in self._db.execute(self._get_insert_query(query)):
                pass

    async def _initialize_table(self) -> None:
        db = self._db  # type:ignore
        create_table = CreateTable(
            table_name="query_logs",
            columns=[
                Column(name="query", data_type="str", is_nullable=False),
                Column(name="timestamp", data_type="int", is_nullable=False)
            ]
        )
        async for _ in db.execute(create_table): pass
        initial_insert = self._get_insert_query(create_table)
        async for _ in db.execute(initial_insert): pass

    def _get_insert_query(self, query: "Query") -> Insert:
        query_str = query.model_dump_json()
        return Insert( table_name="query_logs", values={ "query": query_str, "timestamp": datetime.datetime.now().timestamp() } )