import sys
import importlib
from pathlib import Path
from packaging.version import Version


def api_version():
    return Version("1.0.0")


def import_version(install_prefix):
    install_prefix = Path(install_prefix).expanduser().resolve()
    exepath = install_prefix / "bin" / "Vicar3D"
    libroot = install_prefix / "lib"

    if not exepath.is_file():
        raise RuntimeError(
            f"Target path is not a correctly installed Vicar3D distribution: {install_prefix}, expecting a bin/Vicar3D executable"
        )

    if not libroot.is_dir():
        raise RuntimeError(
            f"Target path is not a correctly installed Vicar3D distribution: {install_prefix}, expecting a lib/ folder"
        )

    sys.path.insert(0, str(libroot))
    try:
        addons_mod = importlib.import_module("pyvicar_addons")
    finally:
        sys.path.pop(0)

    ver_self = api_version()
    try:
        ver_min = addons_mod.min_api_version()
    except AttributeError:
        raise RuntimeError(
            "Target not correctly installed, expecting a min_api_version function in lib/pyvicar_addons module root"
        )
    try:
        ver_max = addons_mod.max_api_version()
    except AttributeError:
        raise RuntimeError(
            "Target not correctly installed, expecting a max_api_version function in lib/pyvicar_addons module root"
        )

    if ver_self < ver_min:
        raise RuntimeError(
            f"Not compatible with the target, requiring higher pyvicar version >= v{ver_min}, but using v{ver_self}"
        )

    if ver_self >= ver_max:
        raise RuntimeError(
            f"Not compatible with the target, requiring lower pyvicar version < v{ver_max}, but using v{ver_self}"
        )

    try:
        Case = addons_mod.case.Case
    except AttributeError:
        raise RuntimeError(
            "Target not correctly installed, expecting a Case class in lib/pyvicar_addons/case module"
        )

    @property
    def runpath(self):
        return exepath

    Case.runpath = runpath

    return Case
