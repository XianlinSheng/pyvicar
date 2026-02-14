import sys
import importlib
from pathlib import Path


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

    try:
        Case = addons_mod.case.Case
    except AttributeError:
        raise RuntimeError(
            "Target version not compatible or not correctly installed, expecting a Case class in lib/pyvicar/case module"
        )

    @property
    def runpath(self):
        return exepath

    Case.runpath = runpath

    return Case
