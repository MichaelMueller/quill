# builtin
import os, sys, tempfile
from typing_extensions import Literal, Optional
# 3rd party
import pytest
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from quill import SqliteDatabase, CreateTable, Column, Transaction, Insert, Update, Delete, Select, \
    Comparison, ColumnRef, And, Or, Length, WriteOperation, Query, Database, Module, QueryLog



class SqliteDatabaseTest: 
    
    @pytest.mark.asyncio
    async def test_in_memory(self):
        try:
            db = SqliteDatabase(":memory:")
            await self._run(db)
        finally:
            await db.close()

    @pytest.mark.asyncio
    async def test_unknown_temp(self):
        try:
            db = SqliteDatabase("")
            await self._run(db)
        finally:
            await db.close()
            
    @pytest.mark.asyncio
    async def test_temp(self):
        temp_db = os.path.join(project_path, "tmp", "test_temp.sqlite3")
        try:
            if os.path.exists(temp_db):
                os.remove(temp_db)
            os.makedirs(os.path.dirname(temp_db), exist_ok=True)
            db = SqliteDatabase(temp_db)
            await self._run(db)
        finally:
            os.remove(temp_db)

    async def _run(self, db:SqliteDatabase):
        
        class GeneralModule(Module):
            def __init__(self, db:"Database"):
                super().__init__(db)
                self._hook_count = 0

            async def __call__(self, query:Query, before_execute:bool) -> None:
                self._hook_count += 1
                #print(f"Module on op: {op.model_dump_json()}")

        await db.register_module(GeneralModule)
        with pytest.raises(ValueError):
            await db.register_module(GeneralModule)
        await db.unregister_module(GeneralModule)
        await db.register_module(GeneralModule)

        await db.register_module(QueryLog)

        create_user_table = CreateTable(
            table_name="user",
            columns=[
                Column(name="name", data_type="str", is_nullable=False),
                Column(name="age", data_type="int", is_nullable=True, default=18)
            ],
            if_not_exists=True
        )

        inserted_ids_or_affected_columns = [x async for x in db.execute(create_user_table)]
        assert len(inserted_ids_or_affected_columns) == 1
        assert inserted_ids_or_affected_columns[0] == -1   # -1 means "not applicable"
        
        # Insert
        transaction = Transaction(items=[
            Insert(
                table_name="user",
                values={"name": "Alice", "age": 31}
            ),
            Insert(
                table_name="user",
                values={"name": "Bob", "age": 29}
            ),
            Insert(
                table_name="user",
                values={"name": "Charlie"}   # age will use default value 18
            )
        ])
        inserted_ids_or_affected_columns = [x async for x in db.execute(transaction)]
        assert len(inserted_ids_or_affected_columns) == 3
        assert inserted_ids_or_affected_columns[0] == 1
        assert inserted_ids_or_affected_columns[1] == 2
        assert inserted_ids_or_affected_columns[2] == 3
        
        # select
        select = Select(
            table_names=["user"],
            columns=["id", "name", "age"],
            order_by="id",
            order="desc"
        )
        data = [x async for x in db.execute(select)]
        assert len(data) == 3
        assert data[2] == (1, "Alice", 31)
        assert data[1] == (2, "Bob", 29)
        assert data[0] == (3, "Charlie", 18)
                
        # Complex select: filter and aggregate
        select_complex = Select(
            table_names=["user"],
            columns=["*"],
            where=Comparison(left=ColumnRef(name="age"), operator=">=", right=29),
            limit=1
        )
        result = [x async for x in db.execute(select_complex)]
        assert len(result) == 1
        assert result[0] == (1, "Alice", 31)
        assert result[0][2] == 31  # Average age of Alice (31) and Bob (29)

if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))