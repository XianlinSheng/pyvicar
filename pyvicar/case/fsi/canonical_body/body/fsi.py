from pyvicar._utilities import Optional
from pyvicar._tree import Group, Field
from pyvicar._file import Writable
from pyvicar._format import KV1Formatter


class FSI(Group, Writable, Optional):
    def __init__(self, f, defaulton=False):
        Optional.__init__(self, defaulton)
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.youngsMod = Field("youngsMod", 1000.0)
        self._children.thickness = Field("thickness", 0.01)
        self._children.damping = Field("damping", 0.0)
        self._children.nu = Field("nu", 0.4)
        self._children.vmass = Field("vmass", 0.0)
        self._children.GMod = Field("GMod", 4.032e-3)

        self._children.forceOpt = Field("forceOpt", 1)
        self._children.dirichletBCOpt = Field("dirichletBCOpt", 0)

        self._children.forceX = Field("forceX", 0)
        self._children.forceY = Field("forceY", 0)
        self._children.forceZ = Field("forceZ", 0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.youngsMod
        self._formatter += self._children.thickness
        self._formatter += self._children.damping
        self._formatter += self._children.nu
        self._formatter += self._children.vmass
        self._formatter += self._children.GMod
        self._formatter.splittext = "|-fsi"
        self._formatter.write()
        self._formatter.splittext = " |-"

        self._formatter += self._children.forceOpt
        self._formatter += self._children.dirichletBCOpt
        self._formatter.write()

        self._formatter += self._children.forceX
        self._formatter += self._children.forceY
        self._formatter += self._children.forceZ
        self._formatter.write()
