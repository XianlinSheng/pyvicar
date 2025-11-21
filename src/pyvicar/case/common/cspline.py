import numpy as np
from pathlib import Path
from pyvicar._utilities import Optional
from pyvicar._tree import Group, Field, List
from pyvicar.file import Writable
from pyvicar._format import KV1Formatter, DatasetFormatter


class CSpline(Group, Writable, Optional):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)
        Optional.__init__(self)
        self._path = Path(path)
        if self:
            self._init()

    def _init(self):
        self._f = open(self._path, "w")
        self._formatter = KV1Formatter(self._f)

        self._children.ncsp = Field("ncsp", 0)
        self._children.csps = Surfaces(self._f)

        self._finalize_init()

    def enable(self):
        Optional.enable(self)
        self._init()

    def write(self):
        if not self:
            raise Exception(f"The object is not active, call .enable() to enable it")

        f = self._f

        self._formatter += self._children.ncsp
        self._formatter.write()

        f.write("\n")

        self._children.csps.write()

        f.flush()


class Surfaces(List, Writable):
    def __init__(self, f):
        List.__init__(self)
        Writable.__init__(self)
        self._f = f

    def _elemcheck(self, new):
        if not isinstance(new, Surface):
            raise TypeError(f"Expected a Surface object, but encountered {repr(new)}")

    def write(self):
        f = self._f

        for surface in self:
            surface.write()
            f.write("\n")

    def appendnew(self, n=1):
        newobjs = [Surface(self._f) for _ in range(n)]
        self._childrenlist += newobjs
        if n == 1:
            return newobjs[0]
        else:
            return newobjs

    def resetnew(self, n=1):
        self._childrenlist = [Surface(self._f) for _ in range(n)]


class Surface(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._f = f
        self._headerFormatter = KV1Formatter(f)
        self._arrayFormatter = DatasetFormatter(f)
        self._headerFormatter.kvtabN = self._arrayFormatter.tabN

        self._children.iBody = Field("iBody", 0)
        self._children.nPoint = Field("nPoint", 0)
        self._children.nElem = Field("nElem", 0)
        self._children.nSeg = Field("nSeg", 0)
        self._children.time = Field("time", 0.0)
        self._children.periodic = Field(
            "periodic", True, "", Field.vmapPresets.bool2int
        )
        self._children.tFrame = Field("tFrame", np.zeros((0, 1), dtype=float))
        self._children.coeff = Field("coeff", np.zeros((0, 4), dtype=float))

        self._finalize_init()

    def write(self):
        f = self._f

        self._headerFormatter += self._children.iBody
        self._headerFormatter.write()

        self._headerFormatter += self._children.nPoint
        self._headerFormatter += self._children.nElem
        self._headerFormatter += self._children.nSeg
        self._headerFormatter.write()

        self._headerFormatter += self._children.time
        self._headerFormatter += self._children.periodic
        self._headerFormatter.write()

        f.write("\n")

        self._arrayFormatter += self._children.tFrame
        self._arrayFormatter.write()

        f.write("\n")

        self._arrayFormatter += self._children.coeff
        self._arrayFormatter.write()
