from pyvicar._tree import Group, Field
from pyvicar._file import Writable
from pyvicar._format import KV2Formatter


class WallTime(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.systemWallTime = Field("systemWallTime", 100.0)
        self._children.exitSafeTime = Field("exitSafeTime", 99.9)
        self._children.iSafeTime = Field(
            "iSafeTime", False, "", Field.vmapPresets.bool2int
        )

        self._finalize_init()

    def write(self):
        self._formatter += self._children.systemWallTime
        self._formatter += self._children.exitSafeTime
        self._formatter += self._children.iSafeTime
        self._formatter.write()
