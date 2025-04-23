from pyvicar.tree.group import Group
from pyvicar.file.io import Writable
from pyvicar.tree.field import Field
from pyvicar.file.formatter import KV2Formatter

class ShearStressSensing(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.nMarker = Field('nMarker', 0)

        self._finalize_init()


    def write(self):
        self._formatter += self._children.nMarker
        self._formatter.write()

