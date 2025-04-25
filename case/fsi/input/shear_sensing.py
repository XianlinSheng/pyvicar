from pyvicar._tree import Group, Field
from pyvicar._file import Writable
from pyvicar._format import KV2Formatter


class ShearStressSensing(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.nMarker = Field("nMarker", 0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.nMarker
        self._formatter.write()
