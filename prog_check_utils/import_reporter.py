"""ImportReporter"""

import builtins
from collections import defaultdict
from types import ModuleType
from typing import Callable, Iterable, Union, Dict, Tuple, List, Any, Optional


class BadImport(Exception):
    """Raised in the case of a forbidden import attempt."""


class ImportReporter:
    """Usage:
    with ImportReporter(arg):
        run some code

    If arg is callable, temporarily redirects all __import__ calls to arg.
    Otherwise, arg is assumed to be an iterable of allowed imports.
    An allowed import can be either:
    - a library name (e.g. "math" allows `import math`);
    - a library name and a name of an entity inside of that library,
      separated by a single slash `/`
      (e.g. "collections/deque" allows `from collections import deque`
       but does not allow `import collections`).
    All __import__ calls have to respect the allowed imports,
    otherwise a BadImport exception is raised."""

    __slots__ = ('orig_import', 'new_import', 'allowed')

    def __init__(self, arg: Union[Callable, Iterable[str]]):
        self.orig_import = builtins.__import__
        # adding _io here as workaround for strange behaviour in Python >= 3.8
        self.allowed: Dict[str, Tuple[str, ...]] = {'_io': ()}
        if callable(arg):
            self.new_import = arg
            return

        self.new_import = self._import
        allowed_entities: Dict[str, List[str]] = defaultdict(list)
        for item in arg:
            lib, _, entity = item.partition('/')
            if entity:
                allowed_entities[lib].append(entity)
            else:
                self.allowed[lib] = ()  # all entities allowed
        self.allowed.update({k: tuple(v)
                             for k, v in allowed_entities.items()})

    # pylint: disable=redefined-builtin,too-many-arguments
    def _import(self, name: str, globals_: Optional[Dict[str, Any]] = None,
                locals_: Optional[Dict[str, Any]] = None,
                fromlist: Optional[List[str]] = None,
                level: int = 0) -> ModuleType:
        if globals_ is None:
            globals_ = {}
        if locals_ is None:
            locals_ = {}
        if fromlist is None:
            fromlist = []

        allowed_entities = self.allowed.get(name)
        if allowed_entities is None:
            raise BadImport(name)

        if allowed_entities:
            if not fromlist:
                raise BadImport(name)

            for entity in fromlist:
                if entity not in allowed_entities:
                    raise BadImport(name, entity)

        # temporarily restore the original __import__ so that
        # the imported library may import other libraries
        with ImportReporter(self.orig_import):
            result = __import__(name, globals_, locals_, fromlist, level)

        if not allowed_entities:
            return result

        module = ModuleType(result.__name__)
        module.__package__ = result.__package__
        for entity in allowed_entities:
            setattr(module, entity, getattr(result, entity))

        return module

    def __enter__(self) -> None:
        builtins.__import__ = self.new_import

    def __exit__(self, *args: Any) -> None:
        builtins.__import__ = self.orig_import
