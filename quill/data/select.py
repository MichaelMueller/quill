# builtin
from typing import Optional, Literal
# 3rd party
import pydantic
# local
from quill.data.query import Query
from quill.data.condition import Condition

class Select(Query):
    type: str = "select"
    table_name: str
    columns: list[str]
    where: Optional[Condition] = None
    
    limit: Optional[int] = None
    offset: Optional[int] = None
    
    sort_by: Optional[str] = None
    sort_order:Optional[Literal["asc","desc"]] = "asc"