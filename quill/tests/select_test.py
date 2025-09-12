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
from quill.ref import Ref
from quill.and_ import And
from quill.or_ import Or
from quill.length import Length

class SelectTest:

    def setup_method(self):
        pass

    def test(self):
        condition = And(
            items=[
                Comparison(
                    left=Ref(table_name="people", name="age"),
                    operator=">",
                    right=18
                ),
                Or(
                    items=[
                        Comparison(
                            left=Ref(table_name="people", name="name"),
                            operator="LIKE",
                            right="A%"
                        ),
                        Comparison(
                            left=Ref(name="name"),
                            operator="LIKE",
                            right="B%"
                        )
                    ]
                )
            ]
        )
        select = Select(
            table_names=["people"],
            columns=["name", "age"],
            where=condition,
            limit=10,
            offset=0,
            order_by=[ ("name", "asc") ]
        )
        sql, params = select.to_sql()
        assert sql.lower() == "select name, age from people where people.age > ? and (people.name like ? or name like ?) order by name asc limit ? offset ?"
        assert params == [18, "A%", "B%", 10, 0]
                
        where = Or(
            items=[
                Comparison(
                left=Ref(name="age"),
                operator="IS",
                right=None),
                Comparison(
                    left=Ref(name="name"),
                    operator="=",
                    right=Ref(name="surname")
                ),
                Comparison(
                    left=Ref(name="id"),
                    operator="IN",
                    right=[1,2,3]
                ),
                Comparison(
                    left=Length(column=Ref(name="name")),
                    operator=">=",
                    right=5
                )
            ]
        )
        select = Select(
            table_names=["people"],
            columns=["id", "name", "surname", "age"],
            where=where
        )
        sql, params = select.to_sql()
        assert sql.lower() == "select id, name, surname, age from people where age is ? or name = surname or id in (?, ?, ?) or length(name) >= ?"
        assert params == [None, 1, 2, 3, 5]

if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))