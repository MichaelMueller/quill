# builtin
from typing import Optional
import importlib
# 3rd party
import pydantic

class DataObject(pydantic.BaseModel):
    main_class:str # fqcn of a related class
    
    def create_instance(self):
        # dynamic import
        # Support inner classes (e.g., quill.tests.data_object_test.DataObjectTest.Calculator)
        parts = self.main_class.split('.')
        if len(parts) < 2:
            raise ValueError("main_class must be at least 'module.ClassName'")
        # Try to find the deepest module that exists
        module:Optional[object] = None
        for i in range(len(parts), 1, -1):
            module_path = '.'.join(parts[:i-1])
            try:
                module = importlib.import_module(module_path)
                break
            except ModuleNotFoundError:
                continue
        if not module:
            raise ModuleNotFoundError(f"Module not found in '{self.main_class}'")
        
        obj = module
        for attr in parts[i-1:]:
            if not hasattr(obj, attr):
                raise AttributeError(f"Attribute '{attr}' not found in '{obj}'")
            obj = getattr(obj, attr)
        cls = obj
        return cls(self)
