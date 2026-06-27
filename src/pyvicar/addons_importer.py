import sys
import importlib
from pathlib import Path
from dataclasses import dataclass
from packaging.version import Version
import pyvicar.tools.log as log


def api_version():
    return Version("1.0.2")


def assert_api_version(ver_min, ver_max):
    if isinstance(ver_min, str):
        ver_min = Version(ver_min)
    if isinstance(ver_max, str):
        ver_max = Version(ver_max)
    ver_self = api_version()
    if ver_self < ver_min:
        raise RuntimeError(
            f"API version not compatible, requiring higher pyvicar version >= v{ver_min}, but using v{ver_self}"
        )

    if ver_self >= ver_max:
        raise RuntimeError(
            f"API version not compatible, requiring lower pyvicar version < v{ver_max}, but using v{ver_self}"
        )


@dataclass
class AddonsPaths:
    root: Path
    bin: Path
    lib: Path
    etc: Path
    exe: Path
    pva: Path
    pva_src: Path
    pva_examples: Path
    modulefiles: Path
    module_vicar3d: Path
    version: str


def import_addons(install_prefix):
    root = Path(install_prefix).expanduser().resolve()
    bin = root / "bin"
    lib = root / "lib"
    etc = root / "etc"
    exe = bin / "ViCar3D"
    pva = lib / "pyvicar_addons"
    pva_src = pva / "src"
    pva_examples = pva / "examples"
    modulefiles = etc / "modulefiles"
    modulefiles_vicar3d = modulefiles / "vicar3d"

    if not root.is_dir():
        raise RuntimeError(f"Specified import path {root} does not exist")

    # # [v1.1.0 reserved] currently optional, will be mandatory starting at v1.1.0
    # if not etc.is_dir():
    #     raise RuntimeError(
    #         f"Target path is not a correctly installed ViCar3D distribution: {install_prefix}, expecting a etc/ folder"
    #     )

    if not exe.is_file():
        raise RuntimeError(
            f"Target path is not a correctly installed ViCar3D distribution: {install_prefix}, expecting a bin/ViCar3D executable"
        )

    if not pva_src.is_dir():
        raise RuntimeError(
            f"Target path is not a correctly installed ViCar3D distribution: {install_prefix}, expecting a lib/pyvicar_addons/src/ pyvicar support impl folder"
        )

    # [v1.1.0 reserved] currently optional, will be mandatory starting at v1.1.0
    if not modulefiles_vicar3d.is_dir():
        log.log(
            f"Note: Starting from pyvicar-v1.1.0 every ViCar3D install needs an etc/modulefiles/vicar3d/version config file to load and set required env modules and variables"
        )
        # raise RuntimeError(
        #     f"Target path is not a correctly installed ViCar3D distribution: {install_prefix}, expecting a etc/modulefiles/vicar3d env modules folder"
        # )

    modulefiles_branch = [p for p in modulefiles_vicar3d.iterdir()]

    # this outter if branch can be removed from v1.1.0
    if modulefiles_vicar3d.is_dir():
        if len(modulefiles_branch) != 1:
            raise RuntimeError(
                f"Target path is not a correctly installed ViCar3D distribution: {install_prefix}, etc/modulefiles/vicar3d should contain exactly one env config file named by the ViCar3D version"
            )
        version = modulefiles_branch[0].stem
    else:
        version = "none"

    sys.path.insert(0, str(pva_src))
    try:
        addons_mod = importlib.import_module("pyvicar_addons")
    except AttributeError:
        raise RuntimeError(
            "Target not correctly installed, expecting an importable module at lib/pyvicar_addons/src/pyvicar_addons"
        )
    finally:
        sys.path.pop(0)

    try:
        ver_min = addons_mod.min_api_version()
    except AttributeError:
        raise RuntimeError(
            "Corrupted addons, expecting a min_api_version function in lib/pyvicar_addons/src/pyvicar_addons module root"
        )

    try:
        ver_max = addons_mod.max_api_version()
    except AttributeError:
        raise RuntimeError(
            "Corrupted addons, expecting a max_api_version function in lib/pyvicar_addons module root"
        )

    assert_api_version(ver_min, ver_max)

    return addons_mod, AddonsPaths(
        root,
        bin,
        lib,
        etc,
        exe,
        pva,
        pva_src,
        pva_examples,
        modulefiles,
        modulefiles_vicar3d,
        version,
    )
