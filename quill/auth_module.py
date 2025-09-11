# builtin
import token
from typing import Optional, Union, AsyncGenerator, TYPE_CHECKING, Literal, cast
from typing import Dict, Union, Any
import os, datetime, sys
from pathlib import Path
# 3rd party
import jwt
# local
from quill import Module, Select, Transaction, GroupModule, UserModule, Database, CreateTable, Column, CreateIndex, ColumnRef, Comparison


class AuthModule(Module):
    CONFIG_TABLE_NAME = "auth_config"    
    CONFIG_USER_AUTH_TYPE_TABLE_NAME = "user_auth_types"    
    
    def __init__(self, db: "Database"):
        super().__init__(db)

    def priority(self) -> int:
        return sys.maxsize
    
    async def _initialize(self) -> None:
        await self._db.register_module(UserModule, exists_ok=True)
        await self._db.register_module(GroupModule, exists_ok=True)
        
        # create tables        
        create_config_table = CreateTable(
            table_name=self.CONFIG_TABLE_NAME,
            columns=[
                Column(name="js", data_type="str", is_nullable=False),  
                Column(name="js_is_file", data_type="bool", is_nullable=False),  
                Column(name="expire_minutes", data_type="int", is_nullable=False, default=15),
                Column(name="issuer", data_type="str", is_nullable=True, default=None),          
            ],
            if_not_exists=True
        )
                
        create_user_auth_types_table = CreateTable(
            table_name=self.CONFIG_USER_AUTH_TYPE_TABLE_NAME,
            columns=[
                Column(name="user_id", data_type="int", is_nullable=False),  
                Column(name="type", data_type="str", is_nullable=False),                
            ],
            if_not_exists=True
        )
        create_user_auth_types_table_user_id_index = CreateIndex(
            table_name=self.CONFIG_USER_AUTH_TYPE_TABLE_NAME,
            columns=["user_id"],
            unique=True,
            if_not_exists=True
        )
        tx = Transaction(items=[create_config_table, create_user_auth_types_table, create_user_auth_types_table_user_id_index])
        async for _ in self._db.execute(tx): pass

    async def before_execute(self, query:Union[Select, Transaction]) -> None:
        jwt_str = getattr(query, "jwt", None)
        if jwt_str is not None:
            _, user_id = await self.decode_jwt(jwt_str)
            current_user = await self._db.by_id("users", user_id)
            current_user = self._db.module(UserModule).row_as_dict(current_user) if current_user else None
            if current_user is None:
                raise ValueError(f"User with id {user_id} not found")
            if current_user["active"] is False:
                raise ValueError(f"User with id {user_id} is not active")
            
            setattr(query, "current_user", current_user)
        else:
            setattr(query, "current_user", None)

    async def generate_jwt(self, user_id: int) -> str:
        config = await self._db.first( Select(table_names=[self.CONFIG_TABLE_NAME]) )
        """Generate a signed JWT."""
        _, js, js_is_file, expire_minutes, issuer = config
        if js_is_file:
            key = Path(js).read_text(encoding="utf-8")
        else:
            key = js

        now = datetime.datetime.now(datetime.timezone.utc)

        claims = {
            "sub": str(user_id),
            "iat": now,
            "exp": now + datetime.timedelta(minutes=expire_minutes),
        }
        if issuer:
            claims["iss"] = issuer
        algorithm = "RS256" if js_is_file else "HS256"
        token = jwt.encode(claims, key, algorithm=algorithm)
        return token

    async def decode_jwt(self,jw_token: str) -> Dict[str, Any]:
        config = await self._db.first( Select(table_names=[self.CONFIG_TABLE_NAME]) )
        _, js, js_is_file, _, issuer = config
        if js_is_file:
            key = Path(js).read_text(encoding="utf-8")
        else:
            key = js

        algorithm = "RS256" if js_is_file else "HS256"
        payload = jwt.decode(
            jw_token,
            key,
            algorithms=[algorithm],
            issuer=issuer if issuer else None,
        )
        return payload, int(payload["sub"])
    