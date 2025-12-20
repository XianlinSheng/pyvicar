from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter


class ParallelConfiguration(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.npx = Field("npx", 2, "n processes in x")
        self._children.npy = Field("npy", 2, "n processes in y")
        self._children.npz = Field("npz", 2, "n processes in z")

        self._children.ngl = Field("ngl", 2, "ghost layer thickness")
        self._children.graphOn = Field("iGraph", True, "", Field.vmapPresets.bool2int)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.npx
        self._formatter += self._children.npy
        self._formatter += self._children.npz
        self._formatter.write()

        self._formatter += self._children.ngl
        self._formatter += self._children.graphOn
        self._formatter.write()
