# builtin
import os, sys
# 3rd party
import pytest
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from quill import Database, DbParams, Module, Transaction, CreateTable, Column, CreateIndex, RenameTable, DropIndex, DropTable, \
    Insert, Update, Delete, Select, Comparison, Ref

class DatabaseTest: 
    
    @pytest.mark.asyncio
    async def test(self):       
        
        params = DbParams(driver="sqlite", db_url=":memory:")
        await self._run_with_different_params(params)
        
        params = DbParams(driver="sqlite", db_url="")
        await self._run_with_different_params(params)
        
        # known file-based db
        temp_db = os.path.join(project_path, "tmp", "test_temp.sqlite3")
        try:
            if os.path.exists(temp_db):
                os.remove(temp_db)
            os.makedirs(os.path.dirname(temp_db), exist_ok=True)
            params = DbParams(driver="sqlite", db_url=temp_db)
            await self._run_with_different_params(params)
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)

    async def _run_with_different_params(self, params:DbParams):
        try:
            db = Database(params)
            await self._run(db)
        finally:
            await db.close()
            
    async def _run(self, db:Database):
        # MODULE tests
        class MyModule1(Module):
            def __init__(self, db: "Database", name:str):
                super().__init__(db)
                
            async def _initialize(self) -> None:
                pass
        
        await db.register_module(MyModule1, args={"name":"module1"})    
        my_module1 = db.module(MyModule1)
        assert my_module1 is not None
        assert isinstance(my_module1, MyModule1)
        
        # DDL Tests
        await self._create_users_table(db)
        rename_table = RenameTable(table_name="users", new_table_name="app_users")        
        inserted_ids_and_affected_rows = [ r async for r in db.execute(rename_table) ]
        assert inserted_ids_and_affected_rows == [ None ]
        await self._delete_users_table(db, table_name="app_users")
        
        # DML Tests
        await self._create_users_table(db)
        insert = Insert(
            table_name="users",
            values={
                "uid": "user1",
                "name": "User One",
                "email": "user1@example.com"
            }
        )
        inserted_ids_and_affected_rows = [ r async for r in db.execute(insert) ]
        assert inserted_ids_and_affected_rows == [ 1 ]
        
        insert2 = Insert(
            table_name="users",
            values={
                "uid": "user2",
                "name": "User Two",
                "email": "user2@example.com"
            }
        )
        inserted_ids_and_affected_rows = [ r async for r in db.execute(insert2) ]
        assert inserted_ids_and_affected_rows == [ 2 ]
        
        insert3 = Insert(
            table_name="users",
            values={
                "uid": "user3",
                "name": "User Three",
                "email": "user3@example.com"
            }
        )
        inserted_ids_and_affected_rows = [ r async for r in db.execute(insert3) ]
        assert inserted_ids_and_affected_rows == [ 3 ]

        insert4 = Insert(
            table_name="users",
            values={
                "uid": "user4",
                "name": "User Four",
                "email": "user4@example.com"
            }
        )
        inserted_ids_and_affected_rows = [ r async for r in db.execute(insert4) ]
        assert inserted_ids_and_affected_rows == [ 4 ]

        update = Update(
            table_name="users",
            values={
                "email": "user1_updated@example.com"
            },
            id=1
        )
        inserted_ids_and_affected_rows = [ r async for r in db.execute(update) ]
        assert inserted_ids_and_affected_rows == [ 1 ]
        
        delete = Delete(
            table_name="users",
            ids=[2]
        )
        inserted_ids_and_affected_rows = [ r async for r in db.execute(delete) ]
        assert inserted_ids_and_affected_rows == [ 1 ]
        
        # SELECT tests
        select = Select(
            table_names=["users"],
            where=Comparison(left=Ref(name="id"), operator=">", right=0),
            order_by=[("id", "asc")]
        )
        user_rows:list[tuple] = [ r async for r in db.execute(select) ]
        assert user_rows == [ (1, "user1", "User One", "user1_updated@example.com"), (3, "user3", "User Three", "user3@example.com"), (4, "user4", "User Four", "user4@example.com") ]
        
        select.as_dict = True
        user_rows_dicts:list[dict] = [ r async for r in db.execute( select ) ]
        assert user_rows_dicts == [
            {"id":1, "uid":"user1", "name":"User One", "email":"user1_updated@example.com"},
            {"id":3, "uid":"user3", "name":"User Three", "email":"user3@example.com"},
            {"id":4, "uid":"user4", "name":"User Four", "email":"user4@example.com"}
        ]

    async def _delete_users_table(self, db:Database, table_name:str):
        drop_index = DropIndex(table_name=table_name, columns=["uid"], if_exists=True)
        drop_index2 = DropIndex(table_name=table_name, columns=["name"], if_exists=True)
        drop_table = DropTable(table_name=table_name, if_exists=True)
        tx = Transaction(items=[drop_index, drop_index2, drop_table])
        inserted_ids_and_affected_rows = [ r async for r in db.execute(tx) ]
        assert inserted_ids_and_affected_rows == [ None, None, None ]
        
    async def _create_users_table(self, db:Database):
        users_table_name = "users"
        create_users_table = CreateTable(
            table_name=users_table_name,
            columns=[
                Column(name="uid", data_type="str"),
                Column(name="name", data_type="str"),
                Column(name="email", data_type="str", is_nullable=True)
            ],
            if_not_exists=True
        )
        create_users_table_name_index = CreateIndex(
            table_name=users_table_name,
            columns=["uid"],
            unique=True,
            if_not_exists=True
        )
        create_users_table_uid_index = CreateIndex(
            table_name=users_table_name,
            columns=["name"],
            unique=True,
            if_not_exists=True
        )
        tx = Transaction(items=[create_users_table, create_users_table_name_index, create_users_table_uid_index])
        inserted_ids_and_affected_rows = [ r async for r in db.execute(tx) ]
        assert inserted_ids_and_affected_rows == [ None, None, None ]

if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))