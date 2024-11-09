import ast
import importlib.util
from typing import get_type_hints
import array

import pytest
from strategies import type_to_strategy


def generate_test(func_name, func, class_name=None):
    global generated_code
    global return_type_check

    params = ', '.join(type_to_strategy(param[1]) for param in func.items() if param[0] != 'return')
    args = ', '.join(param[0] for param in func.items() if param[0] != 'return')
    return_type = func.get('return', None)

    return_type_check = f"assert isinstance(result, {return_type.__name__})" if return_type else "assert result is not None"
    if return_type == array.array:
        return_type_check = f"assert isinstance(result, array.array)"

    # generated test fonction in methods
    if class_name:
        # Instantiate the class
        generated_code = f"""
@given({params})
def test_{class_name}_{func_name}({args}):
    instance = {class_name}()
    result = instance.{func_name}({args})
    {return_type_check}
"""
    else:
        # Function at module level
        generated_code = f"""
@given({params})
def test_{func_name}({args}):
    result = {func_name}({args})
    {return_type_check}
"""
    return generated_code


def main():
    global test_code
    module_name = 'finaltest'
    file_path = 'finaltest.py'
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
