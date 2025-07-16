from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter


class OutputFormat(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.iFullQ = Field("iFullQ", False, "", Field.vmapPresets.bool2int)
        self._children.nDimFullQ = Field("nDimFullQ", 2)
        self._children.stackSize = Field("stackSize", 100)
        self._children.stackStart = Field("stackStart", 0)
        self._children.markerFullQ = Field(
            "markerFullQ", False, "", Field.vmapPresets.bool2int
        )

        self._finalize_init()

    def write(self):
        self._formatter += self._children.iFullQ
        self._formatter += self._children.nDimFullQ
        self._formatter += self._children.stackSize
        self._formatter += self._children.stackStart
        self._formatter += self._children.markerFullQ
        self._formatter.write()
