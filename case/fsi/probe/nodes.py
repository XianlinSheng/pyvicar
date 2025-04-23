import numpy as np
from pyvicar.tree.group import Group
from pyvicar.file.io import Writable
from pyvicar.tree.field import Field
from pyvicar.file.formatter import KV1Formatter, DatasetFormatter


class Nodes(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._headerFormatter = KV1Formatter(f)
        self._arrayFormatter = DatasetFormatter(f)

        self._children.nProbe = Field('nProbe', 0)
        self._children.ijk = Field('ijk', np.zeros((0, 3)))

        self._finalize_init()


    def write(self):
        self._headerFormatter += self._children.nProbe
        self._headerFormatter.write()

        self._arrayFormatter += self._children.ijk
        self._arrayFormatter.write()

