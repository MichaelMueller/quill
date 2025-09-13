# builtin
from typing import Optional, Union, AsyncGenerator, Callable, Type, Any, Literal, TYPE_CHECKING
# 3rd party
# local
from quill.api_module import ApiModule
from quill.query import Query
from quill.api_session import ApiSession

class Api:
    def __init__(self):        
        self._modules:dict[Type["ApiModule"], "ApiModule"] = {}

    async def register_module(self, module_type:Type["ApiModule"], args:Optional[dict[str, Any]]=None, exists_ok:bool = False) -> None:
        mros = self._module_mros(module_type)
        
        if not exists_ok:
            for mro in mros:
                if mro in self._modules:
                    raise ValueError(f"Cannot register module {module_type.__name__}, because base class {mro.__name__} is already registered")

        module = module_type(self) if args is None else module_type(self, **args)
        await module.initialize()
        for mro in mros:
            self._modules[mro] = module

    def find_modules_for_query(self, query:Query) -> list["ApiModule"]:
        query_mros = set( query.__class__.mro() )
        relevant_modules = [m for m in self._modules.values() if len(m.relevant_query_types().intersection(query_mros))>0]
        # sort by priority
        relevant_modules.sort(key=lambda m: m.priority(), reverse=True)
        return relevant_modules

    def module(self, module_type:Type["ApiModule"]) -> Optional["ApiModule"]:
        return self._modules.get(module_type, None)

    async def unregister_module(self, module_type:Type["ApiModule"]) -> None:
        module = self._modules[module_type] 
        await module.shutdown()
        mros = self._module_mros(module_type)
        for mro in mros:
            del self._modules[mro]
    
    async def __aenter__(self) -> ApiSession:
        return self.session()

    async def __aexit__(self, exc_type, exc, tb) -> None:
        pass
    
    def session(self) -> ApiSession:
        return ApiSession(self)

    async def shutdown(self) -> None:
        for module_type in list(self._modules.keys()):
            await self.unregister_module(module_type)

    def _module_mros(self,module_type:Type["ApiModule"]) -> set[Type["ApiModule"]]:
        mros = set( module_type.mro() )
        mros.remove(object)
        mros.remove(ApiModule)
        return mros