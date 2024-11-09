from typing import get_type_hints, Any, TypeVar, Union

from hypothesis import strategies as st
from hypothesis.extra import numpy as stnumpy
from binarytree import Node
import numpy as np
import array
from collections import deque


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
