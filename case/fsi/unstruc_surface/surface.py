import numpy as np
from pyvicar.tree.group import Group
from pyvicar.file.io import Writable
from pyvicar.tree.field import Field
from pyvicar.file.formatter import KV1Formatter, DatasetFormatter


class Surface(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._f = f
        self._headerFormatter = KV1Formatter(f)
        self._arrayFormatter = DatasetFormatter(f)
        self._arrayFormatter.printidx = True
        self._headerFormatter.kvtabN = self._arrayFormatter.tabN

        self._children.nPoint = Field('nPoint', 0)
        self._children.nElem = Field('nElem', 0)
        self._children.xyz = Field('xyz', np.zeros((0, 3), dtype=float))
        self._children.conn = Field('conn', np.zeros((0, 3), dtype=int))

        self._finalize_init()


    def write(self):
        f = self._f

        self._headerFormatter += self._children.nPoint
        self._headerFormatter += self._children.nElem
        self._headerFormatter.write()

        f.write('\n')

        self._arrayFormatter += self._children.xyz
        self._arrayFormatter += self._children.conn
        self._arrayFormatter.write()
