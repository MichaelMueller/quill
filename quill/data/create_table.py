# builtin
from typing import Optional, Literal
# 3rd party
import pydantic
# local
from quill.data.write_operation import WriteOperation
from quill.data.column import Column
from quill.data.data_object import DataObject

class CreateTable(WriteOperation, DataObject):
    type:Literal["create_table"] = "create_table"
    table_name: str
    columns: list[Column]
    if_not_exists: bool = False

    main_class:Literal["quill.create_table.CreateTable"] = "quill.create_table.CreateTable"