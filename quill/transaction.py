# builtin
from typing import Literal
# 3rd party
import pydantic
# local
from quill.query import Query
from quill.write_operation import WriteOperation

class Transaction(Query):
    type: Literal["transaction"] = "transaction"
    items: list[WriteOperation]