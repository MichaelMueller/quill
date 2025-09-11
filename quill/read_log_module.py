# builtin
from typing import Optional, Union, AsyncGenerator, TYPE_CHECKING, Literal
import os, datetime, sys
# 3rd party
import pydantic
# local
from quill.module import Module, Select, Transaction
from quill.column import Column
from quill.create_table import CreateTable
from quill.insert import Insert
from quill.write_operation import WriteOperation
from quill.select import Select
from quill.delete import Delete
if TYPE_CHECKING:
    from quill.database import Database
    from quill.query import Query

class ReadLogModule(Module):
    TABLE_NAME = "read_logs"
    def __init__(self, db: "Database"):
        super().__init__(db)

    def priority(self) -> int:
        return -sys.maxsize - 1
    
    async def _initialize(self) -> None:
        db = self._db  # type:ignore
        create_table = CreateTable(
            table_name=self.table_name(),
            columns=[
                Column(name="user_id", data_type="int", is_nullable=True, default=None),
                Column(name="payload", data_type="str", is_nullable=False),
                Column(name="timestamp", data_type="float", is_nullable=False)
            ]
        )
        async for _ in db.execute(create_table): pass

    async def after_select(self, query:Select) -> None:
        # process select
        values = {}
        excludes = set( ["type", "current_user"] )
        current_user = getattr(query, "current_user", None)
        values["user_id"] = current_user["id"] if current_user else None # if query has user_id attribute use it
        values["payload"] = query.model_dump_json(exclude=excludes)
        values["timestamp"] = datetime.datetime.now().timestamp()
        
        # append the insert to the end of the transaction
        insert_query = Insert( table_name=self.table_name(), values=values )
        async for _ in self._db.execute(insert_query): 
            pass
        
    def table_name(self) -> str:
        return ReadLogModule.TABLE_NAME