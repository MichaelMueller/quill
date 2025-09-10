# builtin
import os, sys
from typing_extensions import Literal, Optional
# 3rd party
import pytest
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from quill.insert import Insert
from quill.delete import Delete
from quill.update import Update
from quill.transaction import Transaction

class DmlTest: 

    def setup_method(self):
        pass

    def test_insert(self):
        insert = Insert(
            table_name="my_table",
            values={
                "name": "John",
                "age": 30
            }
        )
        sql, params = insert.to_sqlite_sql()
        assert sql.lower() == "insert into my_table (name, age) values (?, ?)"
        assert params == ["John", 30]
        
    def test_delete(self):
        delete = Delete(
            table_name="my_table",
            ids=[1, 2, 3]
        )
        sql, params = delete.to_sqlite_sql()
        assert sql.lower() == "delete from my_table where id in (?, ?, ?)"
        assert params == [1, 2, 3]
        
    def test_update(self):
        update = Update(
            table_name="my_table",
            id=1,
            values={
                "name": "Jane",
                "age": 25
            }
        )
        sql, params = update.to_sqlite_sql()
        assert sql.lower() == "update my_table set name = ?, age = ? where id = ?"
        assert params == ["Jane", 25, 1]   
        
        with pytest.raises(ValueError):
            update = Update(
                table_name="my_table",
                id=1,
                values={"id":2}
            )
            sql, params = update.to_sqlite_sql()
        
    def test_transaction(self):
        transaction = Transaction(
            items=[
                Insert(
                    table_name="my_table",
                    values={
                        "name": "Alice",
                        "age": 28
                    }
                ),
                Update(
                    table_name="my_table",
                    id=1,
                    values={
                        "age": 29
                    }
                ),
                Delete(
                    table_name="my_table",
                    ids=[2, 3]
                )
            ]
        )
        sql, params = transaction.to_sqlite_sql()
        assert sql.lower() == "insert into my_table (name, age) values (?, ?); update my_table set age = ? where id = ?; delete from my_table where id in (?, ?);"
        assert params == ["Alice", 28, 29, 1, 2, 3]
        
if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))