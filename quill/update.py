# builtin
from typing import Optional, Literal, Any
# 3rd party
import pydantic
# local
from quill.write_operation import WriteOperation
from quill.sql_expression import SUPPORTED_DIALECTS

class Update(WriteOperation):
    type:Literal["update"] = "update"    
    values: dict[str, Optional[Any]]
    id:int
            
    def to_sql(self, dialect:SUPPORTED_DIALECTS="sqlite", params:list[Any]=[]) -> str:
        sql = ""
        
        for col in self.values.keys():
            if col == "id":
                raise ValueError("Cannot update the 'id' column")
            
            sql += f"{", " if sql != '' else ''}{col} = {self.next_placeholder(dialect, params)}" 
            params.append(self.values[col])
            
        sql = f"UPDATE {self.table_name} SET {sql} WHERE id = {self.next_placeholder(dialect, params)}"
        params.append( self.id )
        return sql