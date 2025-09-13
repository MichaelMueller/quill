# builtin
from typing import Literal
# 3rd party
from pydantic import BaseModel

class MysqlDriverParams(BaseModel):
    host:str
    port:int = 3306
    database:str
    user:str
    password:str
    pool_max_size:int = 5
    pool_min_size:int = 1
    charset:str = "utf8mb4"
    use_unicode:bool = True