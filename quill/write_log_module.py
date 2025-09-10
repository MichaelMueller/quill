# builtin
from typing import TYPE_CHECKING
# 3rd party
# local
from quill.abstract_log_module import AbstractLogModule
if TYPE_CHECKING:
    from quill.database import Database

class WriteLogModule(AbstractLogModule):

    def __init__(self, db: "Database"):
        super().__init__(db)

    def _is_write_log(self) -> bool:
        return True