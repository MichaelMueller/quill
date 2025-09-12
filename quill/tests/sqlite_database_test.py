# builtin
import os, sys, tempfile, asyncio
from typing_extensions import Literal, Optional
# 3rd party
import pytest
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from quill import SqliteDatabase, CreateTable, Column, Transaction, Insert, Update, Delete, Select, \
    Comparison, Ref, And, Or, Length, WriteOperation, Query, Database, Module, ReadLogModule, \
    UserModule, WriteLogModule, GroupModule, AuthModule

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
            if os.path.exists(temp_db):
                os.remove(temp_db)

    async def _run(self, db:SqliteDatabase):
        
        class GeneralModule(Module):
            def __init__(self, db:"Database"):
                super().__init__(db)
                self._hook_count = 0

        await db.register_module(GeneralModule)
        with pytest.raises(ValueError):
            await db.register_module(GeneralModule)
        await db.unregister_module(GeneralModule)
        await db.register_module(GeneralModule)

        await db.register_module(ReadLogModule)
        
        await db.register_module(UserModule)
        await db.register_module(UserModule, exists_ok=True)
        await db.register_module(WriteLogModule)
        await db.register_module(GroupModule)

        create_user_table = CreateTable(
            table_name="person",
            columns=[
                Column(name="name", data_type="str", is_nullable=False),
                Column(name="age", data_type="int", is_nullable=True, default=18)
            ],
            if_not_exists=True
        )

        inserted_ids_or_affected_columns = [x async for x in db.execute(create_user_table)]
        assert len(inserted_ids_or_affected_columns) >= 1
        assert inserted_ids_or_affected_columns[0] == -1   # -1 means "not applicable"
        
        # Insert
        transaction = Transaction(items=[
            Insert(
                table_name="person",
                values={"name": "Alice", "age": 31}
            ),
            Insert(
                table_name="person",
                values={"name": "Bob", "age": 29}
            ),
            Insert(
                table_name="person",
                values={"name": "Charlie"}   # age will use default value 18
            )
        ])
        inserted_ids_or_affected_columns = [x async for x in db.execute(transaction)]
        assert len(inserted_ids_or_affected_columns) >= 3
        assert inserted_ids_or_affected_columns[0] == 1
        assert inserted_ids_or_affected_columns[1] == 2
        assert inserted_ids_or_affected_columns[2] == 3
        
        # select
        select = Select(
            table_names=["person"],
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
            table_names=["person"],
            columns=["*"],
            where=Comparison(left=Ref(name="age"), operator=">=", right=29),
            limit=1
        )
        result = [x async for x in db.execute(select_complex)]
        assert len(result) == 1
        assert result[0] == (1, "Alice", 31)
        assert result[0][2] == 31  # Average age of Alice (31) and Bob (29)

        user_module:UserModule = db.module(UserModule)  # type: ignore
        assert user_module is not None
        
        tx = Transaction(items=[
            Insert(
                table_name="users",
                values={"uid": "u1", "name": "Alice", "email": "alice@example.com"}
            ),
            Insert(
                table_name="users",
                values={"uid": "u2", "name": "Bob", "email": "bob@example.com"}
            ),
            Insert(
                table_name="users",
                values={"uid": "u3", "name": "Charlie"}
            )
        ])
        op_users:list[Insert] = tx.find("users")  # type: ignore
        user_inserts:list[Insert] = tx.find("users", Insert)  # type: ignore
        assert len(op_users) == len(user_inserts)
        ids = [ id async for id in user_module.db().execute(tx) ]
        affected_rows = [ ai async for ai in user_module.db().execute( Update( table_name="users", values={"email": "bob_new@example.com"}, id=ids[1] ) ) ]
        assert len(affected_rows) >= 1 and affected_rows[0] == 1
        
        delete = Delete( table_name="users", ids=ids[:2] )
        affected_rows = [ ai async for ai in user_module.db().execute(delete) ]
        assert len(affected_rows) >= 1 and affected_rows[0] == 2
        # await user_module.exec( UserModule.Update(id=id_charlie, name="Bobby") )
        # with pytest.raises(ValueError):
        #     await user_module.exec( "invalid query" )  # type: ignore
        pass

if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))