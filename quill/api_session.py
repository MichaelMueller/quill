# builtin
from typing import Optional, Union, AsyncGenerator, Callable, Type, Any, Literal, TYPE_CHECKING
import logging
# 3rd party
# local
if TYPE_CHECKING:
    from quill.api import Api
    from quill.api_module import ApiModule
from quill.query import Query

class ApiSession:
    def __init__(self, api: "Api"):        
        self._api = api
        self._executed = False
    
    async def execute(self, query:Query) -> Any:     
          
        try:
            top_level_execute = self._executed == False
            self._executed = True
            
            # find relevant modules sorted by priority
            relevant_modules = self._api.find_modules_for_query(query)
            
            if top_level_execute:
                # execute pre_execute hooks
                for module in relevant_modules:
                    await module.pre_execute(query, self)
                    
            # execute main hooks
            result = None
            
            for module in relevant_modules:
                result = await module.execute(query, self)
                                        
            return result
        
        finally:
            if top_level_execute:
                # execute post_execute hooks
                for module in relevant_modules:
                    try:
                        await module.post_execute(query, self)
                    except Exception as e:
                        logging.error(f"Error in post_execute hook of {module}: {e}")
