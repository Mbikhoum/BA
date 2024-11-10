import ast
import importlib.util
from typing import get_type_hints, Union
import array

import pytest
from strategies import type_to_strategy
import sys


def generate_test(func_name, func, class_name=None):
    global generated_code
    global return_type_check

    params = ', '.join(
        type_to_strategy(param[1]) for param in func.items() if param[0] != 'return'
    )
    args = ', '.join(param[0] for param in func.items() if param[0] != 'return')
    return_type = func.get('return', None)

    if hasattr(return_type, '__origin__') and return_type.__origin__ == Union:
        return_checks = " or ".join(
            f"isinstance(result, {rtype.__name__})" if rtype != type(
                None
            ) else "result is None"
            for rtype in return_type.__args__
        )
        return_type_check = f"assert {return_checks}"

    elif hasattr(return_type, '__origin__') and return_type.__origin__ == list:
        # check type of element in the list (par exemple, List[int])
        if len(return_type.__args__) == 1:
            element_type = return_type.__args__[0]
            return_type_check = (
                f"assert isinstance(result, list) and all(isinstance(item, {element_type.__name__}) for item in result)"
            )
    else:
        return_type_check = f"assert isinstance(result, {return_type.__name__})" if return_type else "assert result is not None"



    if return_type == array.array:
        return_type_check = f"assert isinstance(result, array.array)"


    # generated test fonction in methods
    if class_name:
        # Instantiate the class
        # if no parameter with return type
        if not params and return_type is not None:
            params = "just(None)"
            args = "_"
            generated_code = f"""
@given({params})
def test_{class_name}_{func_name}({args}):
    {class_name.lower()} = {class_name}()
    result = {class_name.lower()}.{func_name}()
    {return_type_check}
"""
            return generated_code

        else:
            generated_code = f"""
@given({params})
def test_{class_name}_{func_name}({args}):
    instance = {class_name}()
    result = instance.{func_name}({args})
    {return_type_check}
"""
            return generated_code

    if not class_name:  # Function at module level

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
    sys.path.append('D:/BA/BA/benchmack') #  path of the file to a succesful import # ('D:/BA/BA/benchmack')
    module_name = 'Komplexfunktion'
    file_path = '../benchmack/Komplexfunktion.py'  #../web_gui/pom/pages/kk/kk001.py
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
