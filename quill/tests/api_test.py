# builtin
import os, sys
from typing_extensions import Literal, Optional
# 3rd party
import pytest
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from quill.api import Api, ApiModule, Query, ApiSession

class ApiTest:

    def setup_method(self):
        pass

    @pytest.mark.asyncio
    async def test(self):
        class HelloQuery(Query):
            type:Literal["hello_query"] = "hello_query"
        
        class TestModule(ApiModule):
            def __init__(self, api):
                super().__init__(api)
                self._num_before_executes = 0
                self._num_executes = 0
                self._num_after_executes = 0
                self._priority = 10
            
            async def pre_execute(self, query:Query, session:ApiSession):
                self._num_before_executes += 1
            
            async def execute(self, query:Query, session:ApiSession) -> tuple[int, int, int]:
                self._num_executes += 1
                return self._num_before_executes, self._num_executes, self._num_after_executes

            async def post_execute(self, query:Query, session:ApiSession) -> None:
                self._num_after_executes += 1

            def relevant_query_types(self) -> set[type[Query]]:
                return { HelloQuery }
            
            def priority(self) -> int:
                return self._priority
            
        api = Api()
        await api.register_module(TestModule)
        module = api.module(TestModule)
        assert module is not None
        
        async with api as session:
            await session.execute(HelloQuery())
            await session.execute(HelloQuery())
            await session.execute(HelloQuery())
            num_before, num_executes, num_after = await session.execute(HelloQuery())
            assert num_before == 1
            assert num_executes == 4
            assert num_after == 1
                    
if __name__ == "__main__":
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))