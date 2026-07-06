from pyvicar._tree import List
from pyvicar.file import Readable, Series
from pyvicar._utilities import Optional
import pyvista as pv
import numpy as np
import re
from collections import defaultdict


class CGNSList(List, Readable, Optional):
    def __init__(self, case):
        List.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._case = case

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    def _append(self, *args, **kwargs):
        return super().append(*args, **kwargs)

    def _insert(self, *args, **kwargs):
        return super().insert(*args, **kwargs)

    def _elemcheck(self, new):
        if not isinstance(new, CGNS):
            raise TypeError(
                f"Expected a CGNS object inside CGNSList, but encountered {repr(new)}"
            )

    @property
    def case(self):
        return self._case

    @property
    def latest(self):
        if not self:
            raise Exception(f"CGNS dump list is not active now")

        return self._childrenlist[-1]

    def read(self):
        self.clear()
        series = Series.from_format(
            self._case.path / "FieldsFiles", (r"fields\.(\d+)\.cgns")
        )
        for i, file in enumerate(series):
            cgns = CGNS(file.path, file.idxes[0], i + self._startidx)
            self._append(cgns)

        if series:
            self._enable()

        return series


class CGNS:
    def __init__(self, path, tstep, seriesi):
        self._path = path
        self._tstep = tstep
        self._seriesi = seriesi

    def to_pyvista(self):
        mesh = pv.read(self._path)[0][0][0]
        mesh = combine_xyz_vectors(mesh)
        return mesh

    @property
    def path(self):
        return self._path

    @property
    def tstep(self):
        return self._tstep

    @property
    def seriesi(self):
        return self._seriesi

    def __repr__(self):
        return f"CGNS(tstep = {self._tstep})"


def combine_xyz_vectors(mesh):
    for location in ["point_data", "cell_data"]:
        data = getattr(mesh, location)
        if data is None:
            continue

        arrays = list(data.keys())
        groups = defaultdict(dict)

        # group matching fields by base name
        for name in arrays:
            match = re.match(r"^(.*?)\(([XYZ])\)$", name)
            if match:
                base, comp = match.groups()
                groups[base][comp] = name

        # build vectors
        for base, comps in groups.items():
            if all(k in comps for k in ["X", "Y", "Z"]):

                vx = data[comps["X"]]
                vy = data[comps["Y"]]
                vz = data[comps["Z"]]

                vec = np.column_stack([vx, vy, vz])

                data[base] = vec  # create vector field

                # remove scalar components
                del data[comps["X"]]
                del data[comps["Y"]]
                del data[comps["Z"]]

    return mesh
