# builtin
from typing import Literal
# 3rd party
import pydantic
# local 

class Query(pydantic.BaseModel):    
    type:Literal["select", "transaction"]