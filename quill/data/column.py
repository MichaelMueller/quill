# builtin
from typing import Optional, Literal, Union, Type
# 3rd party
import pydantic
# local
from quill.data.data_object import DataObject

class Column(DataObject):
    name: str
    data_type: Union[Type[str], Type[int], Type[float], Type[bool], Type[bytes]]
    is_nullable: bool = True
    default: Optional[Union[str, int, float, bool, bytes]] = None

    main_class:Literal["quill.column.Column"] = "quill.column.Column"
  