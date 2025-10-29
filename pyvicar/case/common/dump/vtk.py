import pyvista as pv
from dataclasses import dataclass
from abc import ABC, abstractmethod
from pyvicar._tree import List
from pyvicar.file import Readable, Series
from pyvicar._utilities import Optional
from pyvicar.tools.test.fsi.vtk import is_test, SampleVTK, SampleVTM
from pyvicar.tools.vtk import compress_to_vtk
from pyvicar.tools.log import log


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

    def read(self):
        series = Series.from_format(
            self._case.path / "FieldsFiles", r"fields\.(\d+)\.vtm"
        )
        for i, file in enumerate(series):
            if not is_test():
                vtk = VTK(file.path, file.idxes[0], i + self._startidx)
            else:
                vtk = SampleVTK(file.path, file.idxes[0], i + self._startidx)
            self._append(vtk)

        if series:
            self._enable()

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
        if is_test():
            print(
                "VTM Debug: test will not delete vtms. keep_vtm has been forced to True"
            )
            kwargs["keep_vtm"] = True
        compress_to_vtk(self, **kwargs)


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
