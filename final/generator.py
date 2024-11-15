import ast
import importlib.util
from typing import get_type_hints, Union, Literal
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

    # Modify the return type check for NewType
    if hasattr(return_type, '__supertype__'):  # Check for NewType
        base_type = return_type.__supertype__
        return_type_check = f"assert isinstance(result, {base_type.__name__})"

    #For Literal
    if hasattr(return_type, '__origin__') and return_type.__origin__ == Literal:
        literals = ', '.join(repr(arg) for arg in return_type.__args__)
        return_type_check = f"assert result in [{literals}]"

    ####################################################################################################################

    def handle_union_type_check(type_):
        """Manages Union types to check that the element belongs to one of the specified types."""
        if hasattr(type_, '__origin__') and type_.__origin__ == Union:
            # Generate a check for each type in the Union
            return " or ".join(
                f"isinstance(element, {rtype.__name__})" for rtype in type_.__args__
            )
        # If it's not a Union, return a classic check
        return f"isinstance(element, {type_.__name__})"
    ####################################################################################################################



# Union
    if hasattr(return_type, '__origin__') and return_type.__origin__ == Union:
        return_checks = " or ".join(
            f"isinstance(result, {rtype.__name__})" if rtype != type(
                None
            ) else "result is None"
            for rtype in return_type.__args__
        )
        return_type_check = f"assert {return_checks}"

#dict

    elif hasattr(return_type, '__origin__') and return_type.__origin__ == dict:
        # Recursive check for nested dictionaries
        if len(return_type.__args__) == 2:
            key_type, value_type = return_type.__args__
            # If the value_type is a Union, we need to handle each type in the Union
            if hasattr(value_type, '__origin__') and value_type.__origin__ == Union:
                # Check if the value matches one of the types in the Union
                value_checks = " or ".join(
                    f"isinstance(v, {rtype.__name__})" if rtype != type(None) else "v is None"
                    for rtype in value_type.__args__
                )
                return_type_check = (
                    f"assert isinstance(result, dict) and all(isinstance(k, {key_type.__name__}) and ({value_checks}) "
                    f"for k, v in result.items())"
                )
            else:
                # Handle the case where value_type is a simple type (non-Union)
                return_type_check = (
                    f"assert isinstance(result, dict) and all(isinstance(k, {key_type.__name__}) and "
                    f"isinstance(v, {value_type.__name__}) for k, v in result.items())"
                )

    # tuple
    elif hasattr(return_type, '__origin__') and return_type.__origin__ == tuple:
    # Recursive check for nested tuples
        if len(return_type.__args__) > 0:
            element_types = return_type.__args__
            # Build checks for each element in the tuple
            return_type_check = "assert isinstance(result, tuple) and "
            return_type_check += " and ".join(
                f"isinstance(result[{i}], {elem_type.__name__})"
                if not hasattr(elem_type, '__origin__') or elem_type.__origin__ != list
                else f"isinstance(result[{i}], list) and all(isinstance(item, {elem_type.__args__[0].__name__}) for item in result[{i}])"
                for i, elem_type in enumerate(element_types)
            )
    # Handle tuple types
    elif hasattr(return_type, '__origin__') and return_type.__origin__ == tuple:
        checks = [
            f"isinstance(result[{i}], {t.__name__})"
            for i, t in enumerate(return_type.__args__)
        ]
        return " and ".join(checks)


    def recursive_list_check(element_type, level=0):
        """recursive list generation."""
        var_name = f"item{level}"
        if hasattr(element_type, '__origin__') and element_type.__origin__ == list:
            inner_type = element_type.__args__[0]
            # Recursive checking for types in the list
            inner_check = recursive_list_check(inner_type, level + 1)
            return f"(isinstance({var_name}, list) and all({inner_check} for {var_name} in {var_name}))"
        else:
            # if Union
            return f"(isinstance({var_name}, {element_type.__name__}) or " + handle_union_type_check(element_type) + ")"
        # list
    if return_type is None:
        return_type_check = ""
    elif hasattr(return_type, '__origin__') and return_type.__origin__ == list:
        # Recursive check for nested lists
        if len(return_type.__args__) == 1:
            element_type = return_type.__args__[0]
            # Check if the element type is a custom class (not a built-in type)
            if isinstance(element_type, type):  # Check if element_type is a class
                return_type_check = (
                    f"assert isinstance(result, list) and all(isinstance(item, {element_type.__name__}) for item in result)"
                )
            else:
                # Start the nested all() checks from the outermost list
                return_type_check = (
                    f"assert isinstance(result, list) and all({recursive_list_check(element_type)} for item0 in result)")

    # # Handle MyList[int] and similar custom types
    # if hasattr(return_type, '__supertype__'):  # Check for NewType
    #     base_type = return_type.__supertype__
    #     return_type_check = f"assert isinstance(result, {base_type.__name__})"

    else:
        return_type_check = f"assert isinstance(result, {return_type.__name__})"





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
    sys.path.append('') #  path of the file to a succesful import # ('D:/BA/BA/benchmack')
    module_name = 'finaltest'
    file_path = 'finaltest.py'  #../web_gui/pom/pages/kk/kk001.py
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
    test_code += "from types import NoneType\n"
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
