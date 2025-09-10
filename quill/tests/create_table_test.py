# builtin
import os, sys
from typing_extensions import Literal, Optional
# 3rd party
import pytest
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from quill.create_table import CreateTable, CreateTableData, ColumnData

class CreateTableTest: 

    def setup_method(self):
        pass

    def test(self):
        data = CreateTableData(
            table_name="my_table",
            columns=[
                ColumnData(name="name", data_type=str, is_nullable=False),
                ColumnData(name="age", data_type=int, is_nullable=True, default=18)
            ],
            if_not_exists=True
        )
        create_table = CreateTable(data)
        sql, params = create_table.to_sqlite_sql()
        assert sql.lower() == "create table if not exists my_table (id integer primary key autoincrement, name text not null, age integer default ?)"
        assert params == [18]
        
if __name__ == "__main__":    
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))