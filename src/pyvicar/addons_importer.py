import sys
import importlib
from pathlib import Path
from dataclasses import dataclass
from packaging.version import Version


def api_version():
    return Version("1.0.0")


@dataclass
class AddonsPaths:
    root: Path
    bin: Path
    lib: Path
    exe: Path
    pva: Path
    pva_src: Path
    pva_examples: Path


def import_addons(install_prefix):
    root = Path(install_prefix).expanduser().resolve()
    bin = root / "bin"
    lib = root / "lib"
    exe = bin / "ViCar3D"
    pva = lib / "pyvicar_addons"
    pva_src = pva / "src"
    pva_examples = pva / "examples"

    if not bin.is_dir():
        raise RuntimeError(
            f"Target path is not a correctly installed ViCar3D distribution: {install_prefix}, expecting a bin/ folder"
        )

    if not lib.is_dir():
        raise RuntimeError(
            f"Target path is not a correctly installed ViCar3D distribution: {install_prefix}, expecting a lib/ folder"
        )

    if not exe.is_file():
        raise RuntimeError(
            f"Target path is not a correctly installed ViCar3D distribution: {install_prefix}, expecting a bin/ViCar3D executable"
        )

    if not pva.is_dir():
        raise RuntimeError(
            f"Target path is not a correctly installed ViCar3D distribution: {install_prefix}, expecting a lib/pyvicar_addons/ pyvicar support folder"
        )

    if not pva_src.is_dir():
        raise RuntimeError(
            f"Target path is not a correctly installed ViCar3D distribution: {install_prefix}, expecting a lib/pyvicar_addons/src/ pyvicar support impl folder"
        )

    sys.path.insert(0, str(pva_src))
    try:
        addons_mod = importlib.import_module("pyvicar_addons")
    except AttributeError:
        raise RuntimeError(
            "Target not correctly installed, expecting an importable module at lib/pyvicar_addons/src/pyvicar_addons"
        )
    finally:
        sys.path.pop(0)

    ver_self = api_version()

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

    if ver_self < ver_min:
        raise RuntimeError(
            f"Not compatible with the target, requiring higher pyvicar version >= v{ver_min}, but using v{ver_self}"
        )

    if ver_self >= ver_max:
        raise RuntimeError(
            f"Not compatible with the target, requiring lower pyvicar version < v{ver_max}, but using v{ver_self}"
        )

    return addons_mod, AddonsPaths(root, bin, lib, exe, pva, pva_src, pva_examples)
