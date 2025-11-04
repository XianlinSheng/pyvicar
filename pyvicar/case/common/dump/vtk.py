import pyvista as pv
from dataclasses import dataclass
from abc import ABC, abstractmethod
from pyvicar._tree import List
from pyvicar.file import Readable, Series
from pyvicar._utilities import Optional
from pyvicar.tools.test.fsi.vtk import is_test, SampleVTM, SampleVTK, SampleVTR
from pyvicar.tools.vtk import compress_to_vtk, compress_to_vtr, create_ijs_from_forxy
import pyvicar.tools.log as log


class VTKListBase(List, Readable, Optional):
    def __init__(self, case):
        List.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._case = case

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    @abstractmethod
    def _elemcheck(self, new):
        pass

    def _append(self, *args, **kwargs):
        return super().append(*args, **kwargs)

    def _insert(self, *args, **kwargs):
        return super().insert(*args, **kwargs)

    @property
    def case(self):
        return self._case

    @property
    def latest(self):
        if not self:
            raise Exception(f"VTK dump list is not active now")

        return self._childrenlist[-1]

    def _read_impl(self, ext, cls, samplecls):
        self.clear()
        series = Series.from_format(
            self._case.path / "FieldsFiles", (r"fields\.(\d+)\." + ext)
        )
        for i, file in enumerate(series):
            if not is_test():
                vtk = cls(file.path, file.idxes[0], i + self._startidx)
            else:
                vtk = samplecls(file.path, file.idxes[0], i + self._startidx)
            self._append(vtk)

        if series:
            self._enable()

        return series

    @abstractmethod
    def read(self):
        pass


class VTMList(VTKListBase):
    def __init__(self, case):
        VTKListBase.__init__(self, case)

    def _elemcheck(self, new):
        if not isinstance(new, (VTM, SampleVTM)):
            raise TypeError(
                f"Expected a VTM object inside VTMList, but encountered {repr(new)}"
            )

    def read(self):
        self._read_impl("vtm", VTM, SampleVTM)

    def to_vtks(self, **kwargs):
        log.log_host(
            "Warning: VTK might be 130% space of the original multiblocked VTR if the output is still a full structured rectangular domain. Use to_vtrs(npx, npy) to compress down to 25%"
        )
        if is_test():
            log.log_host(
                "VTM Debug: test still converts real fields, but will not delete vtms. keep_vtms has been forced to True"
            )
            kwargs["keep_vtms"] = True
        compress_to_vtk(self, **kwargs)
        self.read()
        self._case.dump.vtk.read()

    def to_vtrs(self, npx, npy, **kwargs):
        if is_test():
            log.log_host(
                "VTM Debug: test still converts real fields, but will not delete vtms. keep_vtms has been forced to True"
            )
            kwargs["keep_vtms"] = True
        compress_to_vtr(self, create_ijs_from_forxy(npx, npy), **kwargs)
        self.read()
        self._case.dump.vtr.read()


class VTKList(VTKListBase):
    def __init__(self, case):
        VTKListBase.__init__(self, case)

    def _elemcheck(self, new):
        if not isinstance(new, (VTK, SampleVTK)):
            raise TypeError(
                f"Expected a VTK object inside VTKList, but encountered {repr(new)}"
            )

    def read(self):
        self._read_impl("vtk", VTK, SampleVTK)


class VTRList(VTKListBase):
    def __init__(self, case):
        VTKListBase.__init__(self, case)

    def _elemcheck(self, new):
        if not isinstance(new, (VTR, SampleVTR)):
            raise TypeError(
                f"Expected a VTR object inside VTRList, but encountered {repr(new)}"
            )

    def read(self):
        self._read_impl("vtr", VTR, SampleVTR)


class VTKBase(ABC):
    def __init__(self, path, tstep, seriesi):
        self._path = path
        self._tstep = tstep
        self._seriesi = seriesi

    @property
    def path(self):
        return self._path

    @property
    def tstep(self):
        return self._tstep

    @property
    def seriesi(self):
        return self._seriesi

    @abstractmethod
    def to_pyvista(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass


class VTM(VTKBase):
    def __init__(self, path, tstep, seriesi):
        VTKBase.__init__(self, path, tstep, seriesi)

    def to_pyvista(self):
        return pv.read(self._path).combine()

    def to_pyvista_multiblock(self):
        return pv.read(self._path)

    def __repr__(self):
        return f"VTM(tstep = {self._tstep})"


class VTK(VTKBase):
    def __init__(self, path, tstep, seriesi):
        VTKBase.__init__(self, path, tstep, seriesi)

    def to_pyvista(self):
        return pv.read(self._path)

    def __repr__(self):
        return f"VTK(tstep = {self._tstep})"


class VTR(VTKBase):
    def __init__(self, path, tstep, seriesi):
        VTKBase.__init__(self, path, tstep, seriesi)

    def to_pyvista(self):
        return pv.read(self._path)

    def __repr__(self):
        return f"VTR(tstep = {self._tstep})"
