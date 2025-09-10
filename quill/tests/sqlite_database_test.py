# builtin
import os, sys
from typing_extensions import Literal, Optional
# 3rd party
import pytest
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from quill import SqliteDatabase, CreateTable, Column, Transaction


class SqliteDatabaseTest: 
    
    @pytest.mark.asyncio
    async def test_in_memory(self):
        try:
            db = SqliteDatabase(":memory:")
            await self._run(db)
        finally:
            await db.close()

    async def test_temp(self):
        try:
            db = SqliteDatabase("")
            await self._run(db)
        finally:
            await db.close()

    async def _run(self, db:SqliteDatabase):
        create_user_table = CreateTable(
            table_name="user",
            columns=[
                Column(name="name", data_type=str, is_nullable=False),
                Column(name="age", data_type=int, is_nullable=True, default=18)
            ],
            if_not_exists=True
        )

        transaction = Transaction(items=[create_user_table])

        await db.execute(transaction)

if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))