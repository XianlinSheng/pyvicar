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
class StatFunc:
    name: str
    f: FunctionType
    mpi_async: bool


def import_func(module_name: str):
    """
    Import a statistics function by module name.

    Example:
        statlib.import_func("dlcurve") -> StatFunc
    """
    try:
        module = _load_module(module_name)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"Module '{module_name}' does not exist in statlib")

    if not hasattr(module, f"stat_{module_name}"):
        raise FunctionNotFoundError(
            f"Function 'stat_{module_name}' not found in module '{module_name}'"
        )

    if not hasattr(module, f"mpi_async"):
        raise MPIAsyncNotFoundError(
            f"Var 'mpi_async' not found in module '{module_name}', need to specify parallel behavior"
        )

    return StatFunc(
        module_name,
        getattr(module, f"stat_{module_name}"),
        getattr(module, f"mpi_async"),
    )
