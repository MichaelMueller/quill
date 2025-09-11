# builtin
from typing import Optional, Union, AsyncGenerator, TYPE_CHECKING, Literal, cast
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
from quill.read_log_module import ReadLogModule
if TYPE_CHECKING:
    from quill.database import Database
    from quill.query import Query

class WriteLogModule(Module):

    def __init__(self, db: "Database"):
        super().__init__(db)

    def priority(self) -> int:
        return -sys.maxsize - 1
    
    async def _initialize(self) -> None:
        db = self._db  # type:ignore
        create_table = CreateTable(
            table_name=self._table_name(),
            columns=[
                Column(name="user_id", data_type="int", is_nullable=True, default=None),
                Column(name="table_name", data_type="str", is_nullable=False),
                Column(name="query", data_type="str", is_nullable=False),
                Column(name="affected_id", data_type="int", is_nullable=True, default=None),
                Column(name="payload", data_type="str", is_nullable=True),
                Column(name="timestamp", data_type="float", is_nullable=False)
            ]
        )
        async for _ in db.execute(create_table): pass

    async def before_execute(self, query:Union[Select, Transaction]) -> None:
        # devide between write and read log
        if isinstance(query, Select):
            return
        # do not log writes to the read log table
        read_log_module:ReadLogModule = self._db.module(ReadLogModule)    
        
        # process transaction
        list_of_items: list[WriteOperation] = query.items.copy() # make copy as we modify items
        for i, item in enumerate(list_of_items):
            if read_log_module and item.table_name == read_log_module.table_name():
                continue  # do not log writes to the read log table
            # create values
            values = {}
            values["user_id"] = query.user_id
            values["query"] = item.type
            values["table_name"] = item.table_name
            excludes = set( ["table_name", "type", "user_id"] )
            
            # special treatment for delete -> make multiple inserts
            ids: list[int] = []
            if isinstance(item, Delete):
                ids.extend(item.ids)
                excludes.add("ids")
            elif hasattr(item, "id"):
                ids.append(getattr(item, "id"))
                excludes.add("id")
            else:
                ids.append(None)
            
            # final values
            values["payload"] = item.model_dump_json(exclude=excludes)
            values["timestamp"] = datetime.datetime.now().timestamp()
            
            for id in ids: # for each affected id create a log
                values["affected_id"] = id
                                
                # append the insert to the end of the transaction
                insert_query = Insert( table_name=self._table_name(), values=values )
                query.items.append(insert_query)

        
    def _table_name(self) -> str:
        return "write_logs"