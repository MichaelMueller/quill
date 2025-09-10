# builtin
from typing import Optional, Union, AsyncGenerator, TYPE_CHECKING
import os, datetime
# 3rd party
import pydantic
import aiosqlite
# local
from quill import Module, Column, CreateTable, CreateIndex, Insert, WriteOperation, Transaction, Update, Query, Database, Update, Delete, Select, QueryLog

class UserModule(Module):
                
    def __init__(self, db: "Database"):
        super().__init__(db)
        self._table_initialized: bool = False

    async def _initialize(self) -> None:
        if not self._table_initialized:
            await self._db.register_module(QueryLog, exists_ok=True)
            create_table = CreateTable(
                table_name="users",
                columns=[
                    Column(name="uid", data_type="str"),
                    Column(name="name", data_type="str"),
                    Column(name="email", data_type="str", is_nullable=True)
                ],
                if_not_exists=True
            )
            create_name_index = CreateIndex(
                table_name="users",
                columns=["uid"],
                unique=True,
                if_not_exists=True
            )
            create_uid_index = CreateIndex(
                table_name="users",
                columns=["name"],
                unique=True,
                if_not_exists=True
            )

            tx = Transaction(items=[create_table, create_name_index, create_uid_index])
            async for _ in self._db.execute(tx): pass
            self._table_initialized = True

    async def on_query(self, query:"Query", before_execute:bool) -> None:
        pass
        # if not before_execute:
        #     return
        
        # if isinstance(query, WriteOperation):
        #     tx = Transaction(items=[query])
        # elif isinstance(query, Transaction):
        #     tx = query
        # else:
        #     return
        # users_ops = tx.find("users")
        # if len(users_ops) == 0:
        #     return
        
        # now = datetime.datetime.now().timestamp()
        # for op in users_ops:
        #     if isinstance(op, Insert):
        #         op.values["created_at"] = now
        #         op.values["updated_at"] = now
        #     elif isinstance(op, Update):
        #         op.values["updated_at"] = now

