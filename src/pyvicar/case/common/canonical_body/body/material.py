from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV1Formatter


class Material(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.densityFluid = Field("densityFluid", 1.0)
        self._children.densitySolid = Field("densitySolid", 100.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.densityFluid
        self._formatter += self._children.densitySolid
        self._formatter.splittext = "|-material"
        self._formatter.write()
        self._formatter.splittext = " |-"
