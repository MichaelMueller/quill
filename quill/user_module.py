# builtin
from typing import Optional, Union, AsyncGenerator, TYPE_CHECKING
import os, datetime
# 3rd party
import pydantic
import aiosqlite
# local
from quill import Module, Column, CreateTable, CreateIndex, Insert, WriteOperation, Transaction, Update, Query, Database, Update, Delete, Select, WriteLogModule

class UserModule(Module):
    TABLE_NAME = "users"
                
    def __init__(self, db: "Database"):
        super().__init__(db)
        self._table_initialized: bool = False

    def row_as_dict(self, row:tuple) -> dict:
        return {
            "id": row[0],
            "uid": row[1],
            "name": row[2],
            "email": row[3],
            "admin": bool(row[4]),
            "active": bool(row[5]),
        }

    async def _initialize(self) -> None:
        create_table = CreateTable(
            table_name=UserModule.TABLE_NAME,
            columns=[
                Column(name="uid", data_type="str"),
                Column(name="name", data_type="str"),
                Column(name="email", data_type="str", is_nullable=True),
                Column(name="admin", data_type="bool", is_nullable=False, default=False),
                Column(name="active", data_type="bool", is_nullable=False, default=True),
            ],
            if_not_exists=True
        )
        create_name_index = CreateIndex(
            table_name=UserModule.TABLE_NAME,
            columns=["uid"],
            unique=True,
            if_not_exists=True
        )
        create_uid_index = CreateIndex(
            table_name=UserModule.TABLE_NAME,
            columns=["name"],
            unique=True,
            if_not_exists=True
        )

        tx = Transaction(items=[create_table, create_name_index, create_uid_index])
        async for _ in self._db.execute(tx): pass
    
    async def before_execute(self, query:Union[Select, Transaction]) -> None:  
        # validation  
        from quill.auth_module import AuthModule    
        auth_module = self._db.module(AuthModule)
        if auth_module is not None:
            affects_user_table = self.TABLE_NAME in query.table_names if isinstance(query, Select) else len(query.find(self.TABLE_NAME)) > 0
            if affects_user_table:
                current_user:dict = getattr(query, "current_user", None)
                if current_user is None or current_user.get("admin", False) is not True:
                    raise ValueError("Only admin users can access or modify the users table")
            