import importlib
from types import FunctionType
from functools import lru_cache
from dataclasses import dataclass


class FunctionNotFoundError(Exception):
    pass


class MPIAsyncNotFoundError(Exception):
    pass


@lru_cache(maxsize=None)
def _load_module(module_name: str):
    return importlib.import_module(f".{module_name}", package=__package__)


@dataclass
class PostFunc:
    name: str
    f: FunctionType
    mpi_async: bool


def import_func(module_name: str):
    """
    Import a postprocess function by module name.

    Example:
        postlib.import_func("draglift") -> returns PostFunc
    """
    try:
        module = _load_module(module_name)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"Module '{module_name}' does not exist in postlib")

    if not hasattr(module, f"post_{module_name}"):
        raise FunctionNotFoundError(
            f"Function 'post_{module_name}' not found in module '{module_name}'"
        )

    if not hasattr(module, f"mpi_async"):
        raise MPIAsyncNotFoundError(
            f"Var 'mpi_async' not found in module '{module_name}', need to specify parallel behavior"
        )

    return PostFunc(
        module_name,
        getattr(module, f"post_{module_name}"),
        getattr(module, f"mpi_async"),
    )
