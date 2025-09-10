# builtin
import os, sys
from typing_extensions import Literal, Optional
# 3rd party
import pytest
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from quill.condition import Condition
from quill.database import Database
from quill.sql_expression import SqlExpression
from quill.select import Select
from quill.transaction import Transaction

class AbstractClassesTest:

    def setup_method(self):
        pass

    @pytest.mark.asyncio
    async def test(self):
        with pytest.raises(NotImplementedError):
            Condition(type="comparison").to_sqlite_sql()
        with pytest.raises(NotImplementedError):
            SqlExpression(type="none").to_sqlite_sql()
            
        db = Database()
        with pytest.raises(NotImplementedError):
            async for _ in db.execute_select(Select(table_names=["people"])):
                pass
        with pytest.raises(NotImplementedError):
            await db.execute_transaction(Transaction(items=[]))  
            
        async def dummy_hook(query:Select):
            pass

        db.register_hook(dummy_hook, "pre_execute", Select, [])
        matched_hooks = db._find_hook("pre_execute", Select, ["people"])
        assert len(matched_hooks) == 1
        matched_hooks = db._find_hook("post_execute", Select, ["people"])
        assert len(matched_hooks) == 0
        
        db.unregister_hook(dummy_hook)
        assert len(db._hooks) == 0
        
if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))