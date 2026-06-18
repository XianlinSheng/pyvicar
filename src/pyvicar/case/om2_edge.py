from pyvicar._tree import Group, List, Field
from pyvicar._utilities.optional import Optional
from pyvicar._format import KV1Formatter, DatasetFormatter
from pyvicar.file import Writable, lazy_open
from pathlib import Path
import numpy as np


# open membrane 2d edge
class OM2Edge(Group, Writable, Optional):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)
        Optional.__init__(self)
        self._path = Path(path)
        self._f = lazy_open(self._path, "w")
        self._headerFormatter = KV1Formatter(self._f)
        self._arrayFormatter = DatasetFormatter(self._f)
        self._arrayFormatter.printidx = False

        if self:
            self._init()

        self._finalize_init()

    def _init(self):
        self._children.om2s = OM2Bodies(self._f)

        self._finalize_init()

    def enable(self):
        Optional.enable(self)
        self._init()

    def write(self):
        self._children.om2s.write()

        self._f.flush()


class OM2Bodies(List, Writable):
    def __init__(self, f):
        List.__init__(self)
        Writable.__init__(self)

        self._f = f

    def _elemcheck(self, new):
        if not isinstance(new, OM2Body):
            raise TypeError(f"Expected an OM2Body object, got {repr(new)}")

    def write(self):
        f = self._f

        for body in self:
            body.write()
            f.write("\n")

    def appendnew(self, n=1):
        newobjs = [OM2Body(self._f) for _ in range(n)]
        self._childrenlist += newobjs
        if n == 1:
            return newobjs[0]
        else:
            return newobjs

    def resetnew(self, n=1):
        self._childrenlist = [OM2Body(self._f) for _ in range(n)]


class OM2Body(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        Optional.__init__(self)
        self._f = f
        self._headerFormatter = KV1Formatter(self._f)
        self._arrayFormatter = DatasetFormatter(self._f)
        self._arrayFormatter.printidx = False

        self._children.nEdgePoint = Field("nEdgePoint", 0)
        self._children.edgePoints = Field("edgePoints", np.zeros((0, 1)))

        self._finalize_init()

    def write(self):
        self._headerFormatter += self._children.nEdgePoint
        self._headerFormatter.write()

        self._arrayFormatter += self._children.edgePoints
        self._arrayFormatter.write()
