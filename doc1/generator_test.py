import ast
import importlib.util
import inspect
from typing import get_type_hints, List, Dict, Tuple, TypeVar, Any, NewType, Callable
from hypothesis.extra import numpy as stnumpy
from binarytree import Node
import numpy as np
import array
from collections import deque
import pytest
from hypothesis import given, strategies as st


def type_to_strategy(annotation, visited_types=None):
    """Converts type annotations to Hypothesis strategies."""
    # for protection agains recursiv call or infinite call
    if visited_types is None:
        visited_types = set()
    if annotation in visited_types:
        raise ValueError(f"infinite recursivity found : {annotation}")

    visited_types.add(annotation)

    # Convertion basic type

    if annotation == int:
        return "st.integers(min_value=-2**31, max_value=2**31-1)"
    elif annotation == float:
        return "st.floats()"
    elif annotation == str:
        return "st.text()"
    elif annotation == bool:
        return "st.booleans()"


    # To handle array

    elif annotation == array.array:
        # match type to hypothesis strategies
        typecode_to_strategy = {
            'i': 'st.integers(min_value=-2**31, max_value=2**31-1)',  # int
            'f': 'st.floats()',  # float
            'd': 'st.floats()',  # double
            'u': 'st.text()',  # String
            'c': 'st.complex_numbers()',  # Nombres complexes
        }
        # dynamique Typecode extraction
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
            typecode = 'i'  # default value

        if typecode in typecode_to_strategy:
            return f"st.builds(array.array, st.just('{typecode}'), st.lists({typecode_to_strategy[typecode]}))"
        else:
            raise ValueError(f"Unsupported array typecode: {typecode}")


    # hadle other complex type

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

    # Type Alias

    elif isinstance(annotation, TypeVar):
        return "st.integers()"  # Default to integers for generic type variables
    elif annotation == Any:
        return "st.one_of(st.integers(), st.floats(), st.text(), st.booleans())"  # Default to any type




    # Node,tree
    elif annotation == Node:
        # Handle the Node type (binary tree node)
        # Assuming a Node has left , right attribute  and a value for the node value
        return "st.builds(Node, st.integers(), st.one_of(st.none(), st.builds(Node, st.integers(), st.none(), " \
               "st.none())), st.one_of(st.none(), st.builds(Node, st.integers(), st.none(), st.none()))) "


    # Dynamic handling for np.ndarray with optional dtype and shape

    elif annotation == np.ndarray:
        dtype = np.float64  # default dtype
        shape = (3, 3)  # default shape if none provided

        # Check if the annotation has `__args__` to specify dtype and shape dynamically
        if hasattr(annotation, '__args__') and annotation.__args__:
            if len(annotation.__args__) > 0 and isinstance(annotation.__args__[0], type):
                dtype = annotation.__args__[0]
            if len(annotation.__args__) > 1 and isinstance(annotation.__args__[1], tuple):
                shape = annotation.__args__[1]

        # Convert dtype to Hypothesis strategy and return the strategy
        dtype_strategy = {
            int: stnumpy.integer_dtypes(),
            float: stnumpy.floating_dtypes(),
            complex: st.just(np.complex128),  # or complex64
        }.get(dtype, stnumpy.floating_dtypes())  # default to float if not specified

        return f"stnumpy.arrays(dtype={dtype_strategy}, shape={shape})"

    elif isinstance(annotation, type) and hasattr(annotation, '__init__'):
        # For user-defined classes, assume they have an __init__ method that we can pass arguments to.
        init_params = get_type_hints(annotation.__init__)
        init_strategies = ', '.join(
            type_to_strategy(param) for param in init_params.values() if param != 'self' and param != 'return')
        return f"st.builds({annotation.__name__}, {init_strategies})"
    visited_types.remove(annotation)
    raise ValueError(f"Unsupported type: {annotation}")


def generate_test(func_name, func):
    # variable
    global generated_code
    global return_type_check

    params = ', '.join(type_to_strategy(param[1]) for param in func.items() if param[0] != 'return')
    args = ', '.join(param[0] for param in func.items() if param[0] != 'return')
    return_type = func.get('return', None)

    return_type_check = f"assert isinstance(result, {return_type.__name__})" if return_type else "assert result is not None"
    if return_type == array.array:
        return_type_check = f"assert isinstance(result, array.array)"

    if return_type == type(None):
        generated_code = f"""
@given({params})
def test_{func_name}({args}):
    result = {func_name}({args})
    assert result is None
"""

    ##
    # place to handel specialcase
    ##
    else:
        generated_code = f"""
@given({params})
def test_{func_name}({args}):
    result = {func_name}({args})
    {return_type_check}
"""

    return generated_code


def main():
    global test_code
    # Load the module dynamicaly
    module_name = 'minitest'
    file_path = '../doc1/minitest.py'
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # Execute and load the module codes

    # Parse the file
    with open(file_path, "r") as source:
        tree = ast.parse(source.read())

    # Extract function definitions
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]

    # important import
    test_code = "from hypothesis import given, strategies as st, settings\n"
    test_code += f"from {module_name} import *\n\n"
    test_code += "from numpy import *\n\n"
    test_code += "import array\n"
    test_code += "from collections import deque\n"
    test_code += "from binarytree import Node\n"
    test_code += "import numpy as np\n\n"
    test_code += "from hypothesis.extra import numpy as stnumpy\n\n"
    test_code += "from hypothesis.extra.numpy import *\n\n"


    # Extract function name + type hint
    for func in functions:
        func_name = func.name
        func_obj = getattr(module, func_name)
        type_hints = get_type_hints(func_obj)

        # send information to the generator
        test_code += generate_test(func_name, type_hints)

    # Write the generated test code to a file
    test_file_path = 'test_' + module_name + '.py'
    with open(test_file_path, 'w') as test_file:
        test_file.write(test_code)

    # Run the generated tests and print the results
    print(f"Running tests in {test_file_path}...")
    result = pytest.main([test_file_path])
    if result == 0:
        print("All tests passed.")
    else:
        print("Some tests failed.")


if __name__ == "__main__":
    main()
