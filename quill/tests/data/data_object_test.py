# builtin
import os, sys
from typing_extensions import Literal, Optional
# 3rd party
import pytest
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
from quill.data.data_object import DataObject

class DataObjectTest: 
        
    class AdderData(DataObject):
        main_class: Literal["quill.tests.data.data_object_test.DataObjectTest.Adder"] = "quill.tests.data.data_object_test.DataObjectTest.Adder"
        left: int
        right: int

    class Adder:
        def __init__(self, data:"DataObjectTest.AdderData"):
            self._data = data
            
        def result(self):
            return self._data.left + self._data.right

    def setup_method(self):
        # pytest calls this before each test method
        self._obj = DataObjectTest.AdderData(left=3, right=5, operation='+')

    def test_create_instance(self):
        calc = self._obj.create_instance()
        assert isinstance(calc, DataObjectTest.Adder)
        assert calc.result() == 8
        
    def test_error_cases(self):
        with pytest.raises(ModuleNotFoundError):
            DataObject(main_class="non.existent.Module").create_instance()
        with pytest.raises(AttributeError):
            DataObject(main_class="quill.tests.data_object_test.NonExistentClass").create_instance()
        with pytest.raises(ValueError):
            DataObject(main_class="InvalidClassName").create_instance()
            

if __name__ == "__main__":    
    # Run pytest against *this* file only
    sys.exit(pytest.main([__file__, "--no-cov"]))