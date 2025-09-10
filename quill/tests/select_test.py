# builtin
import os, sys
from typing_extensions import Literal, Optional
# 3rd party
import pytest
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from quill.select import Select
from quill.comparison import Comparison
from quill.column_ref import ColumnRef
from quill.and_ import And_
from quill.or_ import Or

class SelectTest:

    def setup_method(self):
        pass

    def test(self):
        condition = And_(
            items=[
                Comparison(
                    left=ColumnRef(table_name="my_table", column_name="age"),
                    operator=">",
                    right=18
                ),
                Or(
                    items=[
                        Comparison(
                            left=ColumnRef(table_name="my_table", column_name="name"),
                            operator="LIKE",
                            right="A%"
                        ),
                        Comparison(
                            left=ColumnRef(column_name="name"),
                            operator="LIKE",
                            right="B%"
                        )
                    ]
                )
            ]
        )
        select = Select(
            table_name="my_table",
            columns=["name", "age"],
            where=condition,
            limit=10,
            offset=0,
            order_by="name",
            order="asc"
        )
        sql, params = select.to_sqlite_sql()
        assert sql.lower() == "select name, age from my_table where my_table.age > ? and (my_table.name like ? or name like ?) order by name asc limit ? offset ?"
        assert params == [18, "A%", "B%", 10, 0]

if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))