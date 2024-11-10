import ast
import importlib.util
import inspect
from typing import get_type_hints, Any, TypeVar, Union
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.extra import numpy as stnumpy
from binarytree import Node
import numpy as np
import array
from collections import deque
import pytest


def type_to_strategy(annotation, visited_types=None):
    """Converts type annotations to Hypothesis strategies."""
    # Protect against recursive or infinite calls
    if visited_types is None:
        visited_types = set()
    if annotation in visited_types:
        raise ValueError(f"infinite recursivity found : {annotation}")

    visited_types.add(annotation)

    # Convert basic types
    if annotation == int:
        return "st.integers(min_value=-2**31, max_value=2**31-1)"
    elif annotation == float:
        return "st.floats()"
    elif annotation == str:
        return "st.text()"
    elif annotation == bool:
        return "st.booleans()"

    # Handle arrays
    elif annotation == array.array:
        typecode_to_strategy = {
            'i': 'st.integers(min_value=-2**31, max_value=2**31-1)',
            'f': 'st.floats()',
            'd': 'st.floats()',
            'u': 'st.text()',
            'c': 'st.complex_numbers()',
        }
        if hasattr(annotation, '__args__') and annotation.__args__:
            element_type = annotation.__args__[0]
            if element_type == int:
                typecode = 'i'
            elif element_type == float:
                typecode = 'f'
            elif element_type == complex:
                typecode = 'c'
            elif element_type == str:
                typecode = 'u'
            else:
                typecode = 'i'
        else:
            typecode = 'i'

        if typecode in typecode_to_strategy:
            return f"st.builds(array.array, st.just('{typecode}'), st.lists({typecode_to_strategy[typecode]}))"
        else:
            raise ValueError(f"Unsupported array typecode: {typecode}")


    # Handle more complex types
    elif hasattr(annotation, '__origin__'):
        if annotation.__origin__ == list:
            return f"st.lists({type_to_strategy(annotation.__args__[0])})"
        elif annotation.__origin__ == tuple:
            return f"st.tuples({', '.join(type_to_strategy(arg) for arg in annotation.__args__)})"
        elif annotation.__origin__ == dict:
            key_type = type_to_strategy(annotation.__args__[0])
            value_type = type_to_strategy(annotation.__args__[1])
            return f"st.dictionaries({key_type}, {value_type})"
        elif annotation.__origin__ == deque:
            return f"st.builds(deque, st.lists({type_to_strategy(annotation.__args__[0])}))"
        elif annotation.__origin__ == set:
            return f"st.sets({type_to_strategy(annotation.__args__[0])})"
        elif annotation.__origin__ == Union:
            union_strategies = [type_to_strategy(arg) for arg in annotation.__args__]
            return f"st.one_of({', '.join(union_strategies)})"


    elif isinstance(annotation, TypeVar):
        return "st.integers()"
    elif annotation == Any:
        return "st.one_of(st.integers(), st.floats(), st.text(), st.booleans())"

    # Node (binary tree node)
    elif annotation == Node:
        return "st.builds(Node, st.integers(), st.one_of(st.none(), st.builds(Node, st.integers(), st.none(), st.none())), st.one_of(st.none(), st.builds(Node, st.integers(), st.none(), st.none())))"

    # NumPy arrays
    elif annotation == np.ndarray:
        dtype = np.float64
        shape = (3, 3)

        if hasattr(annotation, '__args__') and annotation.__args__:
            if len(annotation.__args__) > 0 and isinstance(annotation.__args__[0], type):
                dtype = annotation.__args__[0]
            if len(annotation.__args__) > 1 and isinstance(annotation.__args__[1], tuple):
                shape = annotation.__args__[1]

        dtype_strategy = {
            int: stnumpy.integer_dtypes(),
            float: stnumpy.floating_dtypes(),
            complex: st.just(np.complex128),
        }.get(dtype, stnumpy.floating_dtypes())

        return f"stnumpy.arrays(dtype={dtype_strategy}, shape={shape})"


    # Handle user-defined classes
    elif isinstance(annotation, type) and hasattr(annotation, '__init__'):
        init_params = get_type_hints(annotation.__init__)
        init_strategies = ', '.join(
            type_to_strategy(param) for param in init_params.values() if param != 'self' and param != 'return')
        return f"st.builds({annotation.__name__}, {init_strategies})"

    visited_types.remove(annotation)
    raise ValueError(f"Unsupported type: {annotation}")


def generate_test(func_name, func, class_name=None):
    global generated_code
    global return_type_check

    params = ', '.join(type_to_strategy(param[1]) for param in func.items() if param[0] != 'return')
    args = ', '.join(param[0] for param in func.items() if param[0] != 'return')
    return_type = func.get('return', None)

    return_type_check = f"assert isinstance(result, {return_type.__name__})" if return_type else "assert result is not None"
    if return_type == array.array:
        return_type_check = f"assert isinstance(result, array.array)"

    # if not params:
    #     params = "just(None)"
    #     generated_code = f"""
    #     @given({params})
    #     def test_{class_name}_{func_name}({'_'}):
    #         instance = {class_name}()
    #         result = instance.{func_name}({args})
    #         {return_type_check}
    #     """


    #generated test fonction in methods
    if class_name:
        # Instantiate the class
        generated_code = f"""
@given({params})
def test_{class_name}_{func_name}({args}):
    instance = {class_name}()
    result = instance.{func_name}({args})
    {return_type_check}
"""
    else: # Function at module level

        # if no parameter with return type
        if not params and return_type is not None:
            params = "just(None)"
            args = "_"
            generated_code = f"""
@given({params})
def test_{func_name}({args}):
    result = {func_name}()
    {return_type_check}
"""
        return generated_code

    # for standart fonction
    generated_code = f"""
@given({params})
def test_{func_name}({args}):
    result = {func_name}({args})
    {return_type_check}
"""
    return generated_code


def main():
    global test_code
    module_name = 'mytest'
    file_path = 'mytest.py'
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # Execute and load the module code

    # Parse the file
    with open(file_path, "r") as source:
        tree = ast.parse(source.read())

    test_code = "from hypothesis import given, strategies as st, settings\n"
    test_code += f"from {module_name} import *\n\n"
    test_code += "from numpy import *\n\n"
    test_code += "import array\n"
    test_code += "from collections import deque\n"
    test_code += "from binarytree import Node\n"
    test_code += "import numpy as np\n\n"
    test_code += "from hypothesis.extra import numpy as stnumpy\n\n"
    test_code += "from hypothesis.extra.numpy import *\n\n"
    test_code += "from hypothesis.strategies import just"

    # Process classes and functions
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            # Top-level function
            func_name = node.name
            func_obj = getattr(module, func_name)
            type_hints = get_type_hints(func_obj)
            test_code += generate_test(func_name, type_hints)
        elif isinstance(node, ast.ClassDef):
            # Class with methods
            class_name = node.name
            class_obj = getattr(module, class_name)
            for class_node in node.body:
                if isinstance(class_node, ast.FunctionDef):
                    method_name = class_node.name
                    method_obj = getattr(class_obj, method_name)
                    type_hints = get_type_hints(method_obj)
                    test_code += generate_test(method_name, type_hints, class_name)

    # Write the generated test code to a file
    test_file_path = 'test_' + module_name + '.py'
    with open(test_file_path, 'w') as test_file:
        test_file.write(test_code)

    # Run the generated tests and print results
    print(f"Running tests in {test_file_path}...")
    result = pytest.main([test_file_path])
    if result == 0:
        print("All tests passed.")
    else:
        print("Some tests failed.")


if __name__ == "__main__":
    main()
