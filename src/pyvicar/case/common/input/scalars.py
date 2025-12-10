from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter


class Scalars(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.iScalar = Field("iScalar", False, "", Field.vmapPresets.bool2int)
        self._children.iPart = Field("iPart", False, "", Field.vmapPresets.bool2int)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.iScalar
        self._formatter += self._children.iPart
        self._formatter.write()
