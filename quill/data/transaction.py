# builtin
from typing import Optional
# 3rd party
import pydantic
# local
from quill.data.query import Query
from quill.data.write_operation import WriteOperation

class Transaction(Query):
    type: str = "transaction"
    items: list[WriteOperation]