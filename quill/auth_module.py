# builtin
from typing import Optional, Union, AsyncGenerator, TYPE_CHECKING, Literal, cast
import os, datetime, sys
# 3rd party
import pydantic
# local
from quill import Module, Select, Transaction, GroupModule, Database, CreateTable, Column, CreateIndex

class AuthModule(Module):

    def __init__(self, db: "Database"):
        super().__init__(db)

    def priority(self) -> int:
        return sys.maxsize
    
    async def _initialize(self) -> None:
        await self._db.register_module(GroupModule, exists_ok=True)
