# builtin
from typing import Literal
# 3rd party
from pydantic import BaseModel

class PostgresDriverParams(BaseModel):
    host:str
    port:int = 5432
    database:str
    user:str
    password:str
