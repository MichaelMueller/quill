# builtin
from typing import Optional, Union, AsyncGenerator, TYPE_CHECKING, Literal, cast
import os, datetime, sys
# 3rd party
import pydantic
# local
from quill import Module, Select, Transaction, UserModule, Database, CreateTable, Column, CreateIndex, WriteOperation, Insert, Update, Delete, Comparison, Ref

class GroupModule(Module):
    TABLE_NAME = "groups"

    def __init__(self, db: Database):
        super().__init__(db)
    
    async def _initialize(self) -> None:
        await self._db.register_module(UserModule, exists_ok=True)
        
        create_table = CreateTable(
            table_name=GroupModule.TABLE_NAME,
            columns=[
                Column(name="uid", data_type="str"),
                Column(name="name", data_type="str"),       
                Column(name="user_id", data_type="int", is_nullable=True, default=None),                
            ],
            if_not_exists=True
        )
        create_uid_index = CreateIndex(
            table_name=GroupModule.TABLE_NAME,
            columns=["uid"],
            unique=True,
            if_not_exists=True
        )
        create_user_id_index = CreateIndex(
            table_name=GroupModule.TABLE_NAME,
            columns=["user_id"],
            unique=True,
            if_not_exists=True
        )

        tx = Transaction(items=[create_table, create_user_id_index, create_uid_index])
        async for _ in self._db.execute(tx): pass
    
    async def before_execute(self, query:Union[Select, Transaction]) -> None:  
        # validation  
        if not query.affects_table(GroupModule.TABLE_NAME):
            return
        from quill.auth_module import AuthModule    
        auth_module = self._db.module(AuthModule)
        if auth_module is not None:
            current_user:dict = getattr(query, "current_user", None)
            if current_user is None or current_user.get("admin", False) is not True:
                raise ValueError("Only admin users can access or modify the users table")            

    async def after_execute(self, op:WriteOperation, inserted_id_or_affected_rows:Optional[int]=None) -> list[WriteOperation]:        
        new_ops: list[WriteOperation] = []
        
        if op.table_name == UserModule.TABLE_NAME:        
            if isinstance(op, Insert):
                values = {}
                values["uid"] = op.values["uid"]
                values["name"] = op.values["name"]
                values["user_id"] = inserted_id_or_affected_rows
                new_ops.append( Insert( table_name=GroupModule.TABLE_NAME, values=values ) )
                
            elif isinstance(op, Update):
                values = {}
                if "uid" in op.values:
                    values["uid"] = op.values["uid"]
                if "name" in op.values:
                    values["name"] = op.values["name"]
                if len(values.keys()) > 0:
                    related_group_select = Select( table_names=[ GroupModule.TABLE_NAME ], columns=["id"], where=Comparison(left=Ref(name="user_id"), operator="=", right=op.id) )
                    related_group_id:int = await self._db.first( related_group_select, first_col=True )
                    new_ops.append( Update( table_name=GroupModule.TABLE_NAME, values=values, id=related_group_id ) )

            elif isinstance(op, Delete):
                related_group_selects = Select( table_names=[ GroupModule.TABLE_NAME ], where=Comparison(left=Ref(name="user_id"), operator="IN", right=op.ids) )
                related_group_ids:list[int] = [ row[0] async for row in self._db.execute(related_group_selects) ]
                delete_user_group = Delete( table_name=GroupModule.TABLE_NAME, ids=related_group_ids )
                new_ops.append( delete_user_group )
            
        return new_ops