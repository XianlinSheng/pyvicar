from pyvicar._tree import List
from pyvicar.file import Writable
from .body import Body


class Bodies(List, Writable):
    def __init__(self, f):
        List.__init__(self)
        Writable.__init__(self)
        self._f = f

    def _elemcheck(self, new):
        if not isinstance(new, Body):
            raise TypeError(f"Expected a Body object, but encountered {repr(new)}")

    def write(self):
        f = self._f

        for body in self:
            body.write()
            f.write("\n")

    def appendnew(self, n=1):
        newobjs = [Body(self._f) for _ in range(n)]
        self._childrenlist += newobjs
        if n == 1:
            return newobjs[0]
        else:
            return newobjs

    def resetnew(self, n=1):
        self._childrenlist = [Body(self._f) for _ in range(n)]
