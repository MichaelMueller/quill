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
    pool_max_size:int = 5
    pool_min_size:int = 1
    timeout:float = 15.0  # seconds