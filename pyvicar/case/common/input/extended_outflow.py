from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter


class ExtendedOutflow(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.extendedOutFlow = Field(
            "extendedOutflow", False, "", Field.vmapPresets.bool2int
        )
        self._children.xext = Field("xext", 2.0)
        self._children.dampingFactor = Field("dampingFactor", 5.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.extendedOutFlow
        self._formatter += self._children.xext
        self._formatter += self._children.dampingFactor
        self._formatter.write()
