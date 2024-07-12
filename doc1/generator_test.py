import ast
import importlib.util
from typing import get_type_hints, List, Dict, Tuple, TypeVar, Any, NewType
from hypothesis import given, strategies as st, settings
import pytest


def type_to_strategy(annotation):
    """Converts type annotations to Hypothesis strategies."""
    if annotation == int:
        return "st.integers()"
    elif annotation == float:
        return "st.floats()"
    elif annotation == str:
        return "st.text()"
    elif annotation == bool:
        return "st.booleans()"
    elif hasattr(annotation, '__origin__'):
        if annotation.__origin__ == list:
            return f"st.lists({type_to_strategy(annotation.__args__[0])})"
        elif annotation.__origin__ == tuple:
            return f"st.tuples({', '.join(type_to_strategy(arg) for arg in annotation.__args__)})"
        elif annotation.__origin__ == dict:
            key_type = type_to_strategy(annotation.__args__[0])
            value_type = type_to_strategy(annotation.__args__[1])
            return f"st.dictionaries({key_type}, {value_type})"
    elif isinstance(annotation, TypeVar):
        return "st.integers()"  # Default to integers for generic type variables
    elif annotation == Any:
        return "st.one_of(st.integers(), st.floats(), st.text(), st.booleans())"  # Default to any type
    elif isinstance(annotation, type) and hasattr(annotation, '__init__'):
        # For user-defined classes, assume they have an __init__ method that we can pass arguments to.
        init_params = get_type_hints(annotation.__init__)
        init_strategies = ', '.join(
            type_to_strategy(param) for param in init_params.values() if param != 'self' and param != 'return')
        return f"st.builds({annotation.__name__}, {init_strategies})"
    raise ValueError(f"Unsupported type: {annotation}")


def generate_test(func_name, func):
    params = ', '.join(type_to_strategy(param[1]) for param in func.items() if param[0] != 'return')
    args = ', '.join(param[0] for param in func.items() if param[0] != 'return')
    return_type = func.get('return', None)

    if return_type == type(None):
        test_code = f"""
@given({params})
def test_{func_name}({args}):
    result = {func_name}({args})
    assert result is None
"""
    else:
        if func_name == "factorial":
            # Limit the range of integers for factorial to avoid large computation times
            test_code = f"""
@settings(deadline=1000)
@given(st.integers(min_value=0, max_value=20))  # Limiting the range for factorial
def test_{func_name}({args}):
    result = {func_name}({args})
    assert isinstance(result, int) or result is None
"""
        elif func_name == "is_prime":
            # Increase the deadline for is_prime due to the potential high computation time for large numbers
            test_code = f"""
@settings(deadline=1000)
@given(st.integers())
def test_{func_name}({args}):
    result = {func_name}({args})
    assert isinstance(result, bool)
"""
        else:
            return_type_check = f"assert isinstance(result, {return_type.__name__})" if return_type else "assert result is not None"
            test_code = f"""
@given({params})
def test_{func_name}({args}):
    result = {func_name}({args})
    {return_type_check}
"""
    return test_code


def main():
    # Load the module dynamicaly
    module_name = 'sample_test_files'
    file_path = 'sample_test_files.py'
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # Execute and load the module codes

    # Parse the file
    with open(file_path, "r") as source:
        tree = ast.parse(source.read())

    # Extract function definitions
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]

    test_code = "from hypothesis import given, strategies as st, settings\n"
    test_code += f"from {module_name} import *\n\n"

    # Extract function name + type hint
    for func in functions:
        func_name = func.name
        func_obj = getattr(module, func_name)
        type_hints = get_type_hints(func_obj)

        test_code += generate_test(func_name, type_hints)

    # Write the generated test code to a file
    test_file_path = 'generated_tests_sample.py'
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
