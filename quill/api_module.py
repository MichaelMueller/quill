# builtin
from typing import Optional, Any, Set, Type, TYPE_CHECKING
# 3rd party
# local
if TYPE_CHECKING:
    from quill.api import Api
from quill.query import Query
from quill.api_session import ApiSession

class ApiModule:    
    
    def __init__(self, api: "Api"):
        self._api = api
        self._initialized: bool = False
    
    def api(self) -> "Api":
        return self._api
    
    async def initialize(self) -> None:
        if not self._initialized:
            await self._initialize()
        self._initialized = True    
    
    async def shutdown(self) -> None:
        if self._initialized:
            try:
                await self._shutdown()
            finally:
                self._initialized = False
        
    def relevant_query_types(self) -> Set[Type["Query"]]:
        return set()

    def priority(self) -> int:
        return 0
    
    async def _initialize(self) -> None:
        pass

    async def _shutdown(self) -> None:
        pass    
            
    async def pre_execute(self, query:Query, session:ApiSession) -> None:
        pass
        
    async def execute(self, query:Query, session:ApiSession) -> Any:
        pass
            
    async def post_execute(self, query:Query, session:ApiSession) -> None:
        pass