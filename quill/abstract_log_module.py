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
from quill.select import Select
if TYPE_CHECKING:
    from quill.database import Database
    from quill.query import Query

class AbstractLogModule(Module):

    def __init__(self, db: "Database"):
        super().__init__(db)

    def _is_write_log(self) -> bool:
        raise NotImplementedError()
        
    def _table_name(self) -> str:
        return "write_logs" if self._is_write_log() else "read_logs"
    
    async def on_query(self, query:"Query", before_execute:bool) -> None:
        if self._is_write_log() and isinstance(query, Select):
            return
        elif not self._is_write_log() and not isinstance(query, Select):
            return
        
        # avoid recursion!
        if isinstance(query, Insert) and query.table_name == self._table_name():
            return
        
        if before_execute == False:
            async for _ in self._db.execute(self._get_insert_query(query)):
                pass

    async def _initialize(self) -> None:
        db = self._db  # type:ignore
        create_table = CreateTable(
            table_name=self._table_name(),
            columns=[
                Column(name="query", data_type="str", is_nullable=False),
                Column(name="timestamp", data_type="float", is_nullable=False)
            ]
        )
        async for _ in db.execute(create_table): pass
        initial_insert = self._get_insert_query(create_table)
        async for _ in db.execute(initial_insert): pass

    def _get_insert_query(self, query: "Query") -> Insert:
        query_str = query.model_dump_json()
        return Insert( table_name=self._table_name(), values={ "query": query_str, "timestamp": datetime.datetime.now().timestamp() } )