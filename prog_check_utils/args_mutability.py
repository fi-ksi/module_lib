"""Check im/mutability of function args"""

import inspect
from typing import Dict, Callable, Any, Optional, List
from collections.abc import MutableSequence, MutableSet, MutableMapping


def default_args(func: Callable[..., Any]) -> Dict[str, type]:
    """Returns default argument values of a function"""
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def is_mutable_arg_default_value(
        func: Callable[..., Any],
        user_mutable_types: Optional[List[Any]] = None) -> bool:
    """
    Checks if a function 'func' contains any mutable default argument.
    Warning: this function tests only some basic predefined types. Mutabily
    for user-defined types is not possible to check at language-level.
    """
    if user_mutable_types is None:
        user_mutable_types = []
    for default_value in default_args(func).values():
        if issubclass(type(default_value),
                      (MutableSequence, MutableSet, MutableMapping,
                       *user_mutable_types)):
            return True
    return False


def assert_immutable_arg_default_values(
        func: Callable[..., Any],
        user_mutable_types: Optional[List[Any]] = None) -> None:
    """
    Raises AssertionError when mutable default arg value is present in
    a function 'func'.
    """
    assert not is_mutable_arg_default_value(func, user_mutable_types), \
        (f"Funkce '{func.__name__}' obsahuje *mutable* výchozí hodnotu "
         "argumentu!")
