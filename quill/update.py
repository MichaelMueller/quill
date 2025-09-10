# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.write_operation import WriteOperation

class Update(WriteOperation):
    type:Literal["update"] = "update"    
    table_name: str
    values: dict[str, Optional[Any]]
    id:int
            
    def to_sqlite_sql(self) -> tuple[str, list[Any]]:
        sql = ""
        for col in self.values.keys():
            if col == "id":
                raise ValueError("Cannot update the 'id' column")
            sql += f"{", " if sql != '' else ''}{col} = ?" 
        sql = f"UPDATE {self.table_name} SET {sql} WHERE id = ?"
        params = list(self.values.values()) + [self.id]
        return sql, params