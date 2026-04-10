from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter


class LaplaceSolver(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.VDVActive = Field(
            "VDVActive", False, "", Field.vmapPresets.bool2int
        )
        self._children.nVisual = Field("nVisual", 1)
        self._children.itermaxLaplace = Field("itermaxLaplace", 1000)
        self._children.restolLaplace = Field("restolLaplace", 5e-4)
        self._children.idirection = Field(
            "idirection", "x", "", Field.vmapPresets.xyz2int
        )

        self._children.fx1 = Field("fx1", 0.0)
        self._children.fx2 = Field("fx2", 15.0)
        self._children.fy1 = Field("fy1", 0.0)
        self._children.fy2 = Field("fy2", 10.0)
        self._children.fz1 = Field("fz1", 0.0)
        self._children.fz2 = Field("fz2", 5.0)

        self._children.itSolverTypeLaplace = Field(
            "itSolverTypeLaplace", "mg", "", {"linesor": 1, "mg": 2}
        )
        self._children.fQComputeType = Field("fQComputeType", 1)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.VDVActive
        self._formatter += self._children.nVisual
        self._formatter += self._children.itermaxLaplace
        self._formatter += self._children.restolLaplace
        self._formatter += self._children.idirection
        self._formatter.write()

        self._formatter += self._children.fx1
        self._formatter += self._children.fx2
        self._formatter += self._children.fy1
        self._formatter += self._children.fy2
        self._formatter += self._children.fz1
        self._formatter += self._children.fz2
        self._formatter.write()

        self._formatter += self._children.itSolverTypeLaplace
        self._formatter += self._children.fQComputeType
        self._formatter.write()
