from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter


class PoissonSolver(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.itSolverType = Field(
            "itSolverType",
            "pbicgstab",
            "",
            {"linesor": 1, "mg": 2, "pbicgstab": 3, "srj": 4, "cgsrj": 5, "srj2": 6},
        )
        self._children.redblack = Field(
            "red_black", False, "", Field.vmapPresets.bool2int
        )

        self._children.omega = Field("omega", 1.5)

        self._children.itermaxPoisson = Field("itermaxPoisson", 10000)
        self._children.resmaxPoisson = Field("resmaxPoisson", 5e-4)
        self._children.iterresPoisson = Field("iterresPoisson", 5)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.itSolverType
        self._formatter += self._children.redblack
        self._formatter.write()

        self._formatter += self._children.omega
        self._formatter.write()

        self._formatter += self._children.itermaxPoisson
        self._formatter += self._children.resmaxPoisson
        self._formatter += self._children.iterresPoisson
        self._formatter.write()
