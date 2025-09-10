# builtin
from typing import Optional
# 3rd party
import pydantic
# local

class Condition(pydantic.BaseModel):
    type:str = pydantic.Field(discriminator=True) 