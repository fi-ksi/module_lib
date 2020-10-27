"""Various helpers for the KSI checker."""

from contextlib import redirect_stdout, ExitStack
from io import StringIO
import importlib.util
from types import ModuleType, FunctionType
from typing import Iterable, Any, Optional, Callable, Dict, Tuple, List
import functools
import html
import copy
import re

from utils.import_reporter import ImportReporter, BadImport
from utils.args_mutability import assert_immutable_arg_default_values


def exception_str(exc: BaseException) -> str:
    """Return properly exscaped html message of the exception."""
    exc_description = type(exc).__name__
    if exc.args:
        exc_description += ": " + str(exc.args[0])
    if isinstance(exc, ImportError):
        # remove the library path
        exc_description = re.sub(r" \(.*\)", "", exc_description)
    return html.escape(exc_description)


def import_file(name: str, filename: str) -> ModuleType:
    """Import a module from the given file."""
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        return ModuleType(name)
    spec.loader.exec_module(module)  # type: ignore
    return module


def wrap_student_module(filename: str,
                        allowed_libs: Iterable[str],
                        check_stdout: bool = False) -> ModuleType:
    """Import a student module and wrap all calls with ImportReporter.
    This needs Python 3.7.
    If check_stdout is True, asserts that nothing is written on stdout
    during importing.
    """
    c_stdout = StringIO() if check_stdout else None

    with ExitStack() as stack:
        stack.enter_context(ImportReporter(allowed_libs))
        if c_stdout is not None:
            stack.enter_context(redirect_stdout(c_stdout))
        orig_module = import_file('student', filename)

    if c_stdout is not None:
        assert not c_stdout.getvalue(), \
            "Řešení obsahuje kód, který se vykonává mimo funkce."

    wrapped_module = ModuleType('student')

    def __getattr__(name: str) -> Any:
        attr = getattr(orig_module, name)
        if not callable(attr):
            return attr

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with ImportReporter(allowed_libs):
                return attr(*args, **kwargs)

        functools.update_wrapper(wrapper, attr)
        return wrapper

    def get_module_attribute(name: str) -> Any:
        return getattr(orig_module, name)

    def set_module_attribute(name: str, value: Any) -> None:
        setattr(orig_module, name, value)

    setattr(wrapped_module, '__getattr__', __getattr__)
    setattr(wrapped_module, 'set_module_attribute', set_module_attribute)
    setattr(wrapped_module, 'get_module_attribute', get_module_attribute)
    return wrapped_module


def student_function(student_module: ModuleType,
                     func_name: str) -> FunctionType:
    """
    Tries to find function 'func_name' in student's code. It successful,
    it returns the function as callable
    """
    assert hasattr(student_module, func_name), \
        f"Řešení neobsahuje funkci '{func_name}'!"
    student_func = getattr(student_module, func_name)
    assert callable(student_func), \
        f"Řešení neobsahuje funkci '{func_name}'!"
    return student_func  # type: ignore


def _stringify_arg(arg: Any) -> str:
    if isinstance(arg, str):
        return "'" + arg.replace("\\", "\\\\").replace("'", "\\'") + "'"
    return str(arg)


def stringify_args(*args: Any, **kwargs: Any) -> str:
    """
    Returns args & kwargs as a text to be copied directly to a function call.
    Useful for printing counterexamples.
    """
    args_unrolled = html.escape(', '.join(map(_stringify_arg, args)))
    kwargs_unrolled = html.escape(
        ("".join(f", {key}: {_stringify_arg(value)}"
                 for key, value in kwargs.items()))) \
        if kwargs else ''
    return args_unrolled + kwargs_unrolled


def stringify_args_human_readable(*args: Any, **kwargs: Any) -> str:
    """Returns args & kwargs as human-readable string."""
    result = stringify_args(*args, **kwargs)
    if result == '':
        result = '(žádné argumenty)'
    if len(result) > 1000:
        result = result[:1000] + '... (příliš dlouhý vstup)'
    return result


def _reset_args_kwargs(*args: Any, **kwargs: Any) -> None:
    for arg in args:
        if hasattr(arg, 'test_reset'):
            arg.test_reset()
    for kwarg in kwargs.values():
        if hasattr(kwarg, 'test_reset'):
            kwarg.test_reset()


def _student_exec_stdout(student_func: Callable[..., Any], *args: Any,
                         args_str: str, **kwargs: Any) -> Tuple[Any, str]:
    """
    Low-level execute student function and return its result & stdout.

    This function should not be called from outside, because it does not check
    for presence of the __name__, whether student_func is really callable, ...
    """
    try:
        c_stdout = StringIO()
        with redirect_stdout(c_stdout):
            result = student_func(*args, **kwargs)
        return (result, c_stdout.getvalue())
    except BadImport:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        assert False, \
            f"Při pokusu o spuštění funkce '{student_func.__name__}' " \
            f"{args_str} došlo k chybě: " + \
            exception_str(exc)


def student_exec_stdout(student_func: Callable[..., Any],
                        *args: Any,
                        counterexample: bool = True,
                        check_param_ro: bool = True,
                        check_param_immutable: bool = True,
                        user_mutable_types: Optional[List[Any]] = None,
                        **kwargs: Any) -> Tuple[Any, str]:
    """
    Execute student function and return its result & stdout.

    Raise nice assert in case of error.
    Optinal checks:
     * function does not modify its parameters
     * function does not use immutable default value of a parameter
    """
    if not callable(student_func) or not hasattr(student_func, '__name__'):
        assert False, f"Nelze zavolat {str(student_func)}, není funkce!"

    if check_param_immutable:
        assert_immutable_arg_default_values(student_func, user_mutable_types)

    if counterexample:
        str_args = stringify_args_human_readable(*args, **kwargs)
        args_str = f'na vstupu {str_args}'
    else:
        args_str = ''

    if check_param_ro:
        orig_args = copy.deepcopy(args)
        orig_kwargs = copy.deepcopy(kwargs)

    _reset_args_kwargs(*args, **kwargs)

    result = _student_exec_stdout(
        student_func, *args, args_str=args_str, **kwargs
    )

    assert (not check_param_ro or
            (args == orig_args and kwargs == orig_kwargs)), \
        (f"Vaše funkce '{student_func.__name__}' změnila argumenty, což je "
         "zakázáno!")

    return result


def student_exec(student_func: Callable[..., Any],
                 *args: Any,
                 counterexample: bool = True,
                 check_param_ro: bool = True,
                 check_param_immutable: bool = True,
                 user_mutable_types: Optional[List[Any]] = None,
                 **kwargs: Any) -> Any:
    """
    Execute student function and return its result. Function is checked for
    empty stdout.
    """
    result, stdout = student_exec_stdout(
        student_func, *args, counterexample=counterexample,
        check_param_ro=check_param_ro,
        check_param_immutable=check_param_immutable,
        user_mutable_types=user_mutable_types, **kwargs
    )
    assert stdout == '', \
        f"Funkce '{student_func.__name__}' píše na výstup i když nemá psát!"
    return result


def student_test(student_func: Callable[..., Any],
                 teacher_func: Callable[..., Any],
                 *args: Any,
                 counterexample: bool = True,
                 check_param_ro: bool = True,
                 check_param_immutable: bool = True,
                 user_mutable_types: Optional[List[Any]] = None,
                 **kwargs: Any) -> None:
    """Test single student function."""
    if check_param_ro:
        orig_args = copy.deepcopy(args)
        orig_kwargs = copy.deepcopy(kwargs)

    expected = teacher_func(*args, **kwargs)
    assert (not check_param_ro or
            (args == orig_args and kwargs == orig_kwargs)), \
        (f"Učitelská funkce '{teacher_func.__name__}' změnila argumenty, "
         "napište do disk. fóra!")

    result = student_exec(
        student_func, *args, counterexample=counterexample,
        check_param_ro=check_param_ro,
        check_param_immutable=check_param_immutable,
        user_mutable_types=user_mutable_types, **kwargs
    )

    if result != expected:
        if counterexample:
            str_args = stringify_args_human_readable(*args, **kwargs)
            args_str = f'na vstupu {str_args}'
        else:
            args_str = ''
        assert False, \
            (f"Výstup vaši funkce '{student_func.__name__}' {args_str} "
             "neodpovídá očekávánému výstupu.")


def student_mock(module: ModuleType, items: Dict[str, Any]) -> Dict[str, Any]:
    """Mock student names 'items.keys()' to anthing."""
    orig = {
        name: getattr(module, name) for name in items if hasattr(module, name)
    }
    for name, val in items.items():
        module.set_module_attribute(name, val)  # type: ignore
    return orig


def student_restore(module: ModuleType, mocked: Dict[str, Any]) -> None:
    """Restore mocked functions."""
    for name, val in mocked.items():
        module.set_module_attribute(name, val)  # type: ignore
