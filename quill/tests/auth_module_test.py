# builtin
import os, sys, tempfile, asyncio, secrets
from typing_extensions import Literal, Optional
# 3rd party
import pytest
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from quill import SqliteDatabase, Transaction, Insert, AuthModule, UserModule

class AuthModuleTest: 
    
    @pytest.mark.asyncio
    async def test(self):
        try:
            database = SqliteDatabase(":memory:")
            await database.register_module(UserModule)
            tx = Transaction(items=[
                Insert(
                    table_name="users",
                    values={"uid": "alice", "name": "Alice", "email": "alice@example.com"}
                ),
                Insert(
                    table_name="users",
                    values={"uid": "bob", "name": "Bob", "email": "bob@example.com"}
                ),
                Insert(
                    table_name="users",
                    values={"uid": "charlie", "name": "Charlie"}
                )
            ])            
            ids = [ id async for id in database.execute(tx) ]
            
            await database.register_module(AuthModule)
            async for _ in database.execute( Insert(
                    table_name="auth_config",
                    values={"js": secrets.token_urlsafe(32) , "js_is_file": False, "expire_minutes": 60, "issuer": "test_issuer"}
                )): pass
            
            auth_module:AuthModule = database.module(AuthModule)
            jwt = await auth_module.generate_jwt( user_id=1 )
            decoded_jwt, user_id = await auth_module.decode_jwt( jwt )
            assert decoded_jwt["sub"] == "1"
            assert user_id == 1
            assert decoded_jwt["iss"] == "test_issuer"
        finally:
            await database.close()

if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))