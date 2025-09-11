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

    async def after_execute(self, write_operation:WriteOperation, inserted_id_or_affected_rows:Optional[int]=None) -> list[WriteOperation]:
        new_ops: list[WriteOperation] = []
        
        insert_on_write_log = isinstance(write_operation, Insert) and write_operation.table_name == self._table_name()
        handle_op = write_operation.table_name != ReadLogModule.TABLE_NAME and not insert_on_write_log

        if handle_op:

            # create values
            values = {}
            values["user_id"] = getattr(write_operation, "user_id", None) # if write_operation has user_id attribute use it
            values["query"] = write_operation.type
            values["table_name"] = write_operation.table_name
            excludes = set( ["table_name", "type", "user_id"] )
            
            # special treatment for delete -> make multiple inserts
            ids: list[int] = []
            if isinstance(write_operation,Insert):
                ids.append(inserted_id_or_affected_rows)
            elif isinstance(write_operation, Delete):
                ids.extend(write_operation.ids)
                excludes.add("ids")
            elif hasattr(write_operation, "id"):
                ids.append(getattr(write_operation, "id"))
                excludes.add("id")
            else:
                ids.append(None)
            
            # final values
            values["payload"] = write_operation.model_dump_json(exclude=excludes)
            values["timestamp"] = datetime.datetime.now().timestamp()
            
            for id in ids: # for each affected id create a log
                values["affected_id"] = id
                                
                # append the insert to the end of the transaction
                insert_query = Insert( table_name=self._table_name(), values=values )
                new_ops.append(insert_query)

        return new_ops
    
        
    def _table_name(self) -> str:
        return "write_logs"