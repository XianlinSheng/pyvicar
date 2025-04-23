from pyvicar.tree.group import List
from pyvicar.file.io import Writable
from pyvicar.tree.field import Field, Point3D
from pyvicar.file.formatter import DatasetFormatter
from .surface import Surface


class Surfaces(List, Writable):
    def __init__(self, f):
        List.__init__(self)
        Writable.__init__(self)
        self._f = f


    def _elemcheck(self, new):
        if not isinstance(new, Surface):
            raise TypeError(f'Expected a Surface object, but encountered {repr(new)}')


    def write(self):
        f = self._f

        for surface in self:
            surface.write()
            f.write('\n')
        

    def appendnew(self, n=1):
        newobjs = [Surface(self._f) for _ in range(n)]
        self._children += newobjs
        if n == 1:
            return newobjs[0]
        else:
            return newobjs

    
    def resetnew(self, n=1):
        self._children = [Surface(self._f) for _ in range(n)]
