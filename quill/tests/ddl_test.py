# builtin
import os, sys
from typing_extensions import Literal, Optional
# 3rd party
import pytest
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from quill.create_table import CreateTable, Column
from quill.rename_table import RenameTable
from quill.drop_table import DropTable
from quill.create_index import CreateIndex
from quill.drop_index import DropIndex

class DdlTest: 

    def setup_method(self):
        pass

    def test_create_table(self):
        create_table = CreateTable(
            table_name="my_table",
            columns=[
                Column(name="name", data_type=str, is_nullable=False),
                Column(name="age", data_type=int, is_nullable=True, default=18)
            ],
            if_not_exists=True
        )
        sql, params = create_table.to_sqlite_sql()
        assert sql.lower() == "create table if not exists my_table (id integer primary key autoincrement, name text not null, age integer default ?)"
        assert params == [18]
        
    def test_rename_table(self):
        rename_table = RenameTable(
            old_table_name="my_table",
            new_table_name="new_table"
        )
        sql, params = rename_table.to_sqlite_sql()
        assert sql.lower() == "alter table my_table rename to new_table"
        assert params == []

    def test_drop_table(self):
        drop_table = DropTable(
            table="my_table",
            if_exists=True
        )
        sql, params = drop_table.to_sqlite_sql()
        assert sql.lower() == "drop table if exists my_table"
        assert params == []

    def test_create_index(self):
        create_index = CreateIndex(
            table_name="my_table",
            columns=["name"],
            unique=False,
            if_not_exists=True
        )
        sql, params = create_index.to_sqlite_sql()
        assert sql.lower() == "create index if not exists my_table_name_idx on my_table (name)"
        assert params == []
        
        create_unique_index = CreateIndex(
            table_name="my_table",
            columns=["name", "age"],
            unique=True,
            if_not_exists=False
        )
        sql, params = create_unique_index.to_sqlite_sql()
        assert sql.lower() == "create unique index my_table_name_age_uidx on my_table (name, age)"
        assert params == []

    def test_drop_index(self):
        drop_index = DropIndex(
            table_name="my_table",
            columns=["name", "age"],
            unique=True,
            if_exists=True
        )
        sql, params = drop_index.to_sqlite_sql()
        assert sql.lower() == "drop index if exists my_table_name_age_uidx"
        assert params == []

if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))