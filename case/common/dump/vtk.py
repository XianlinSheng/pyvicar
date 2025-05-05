import pyvista as pv
from dataclasses import dataclass
from pyvicar._tree import List
from pyvicar._file import Readable, Series
from pyvicar._utilities import Optional


class VTKList(List, Readable, Optional):
    def __init__(self, case):
        List.__init__(self)
        Readable.__init__(self)
        self._case = case

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    def _elemcheck(self, new):
        if not isinstance(new, VTK):
            raise TypeError(
                f"Expected a VTK object inside VTKList, but encountered {repr(new)}"
            )

    def _append(self, *args, **kwargs):
        return super().append(*args, **kwargs)

    def _insert(self, *args, **kwargs):
        return super().insert(*args, **kwargs)

    def read(self):
        series = Series.from_format(self._case.path / "qFiles", r"fields\.(\d+)\.vtm")
        for i, file in enumerate(series):
            vtk = VTK(file.path, file.idxes[0], i + self._startidx)
            self._append(vtk)

        if series:
            self._enable()

    @property
    def latest(self):
        if not self:
            raise Exception(f"VTKList is not active now")

        return self[self._startidx - 1]


class VTK:
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

    def to_pyvista_multiblocks(self):
        return pv.read(self._path)

    def to_pyvista(self):
        return pv.read(self._path).combine()

    def __repr__(self):
        return f"VTK(tstep = {self._tstep})"
