from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter


class FSI(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.coupling = Field(
            "coupling", "explicit", "", {"explicit": 0, "implicit": 1}
        )
        self._children.implMaxres = Field("implMaxres", 1e-6)
        self._children.implMaxiter = Field("implMaxiter", 10)

        self._children.alpOpt = Field("alpOpt", "no", "", {"no": 1, "v": 2, "am": 3})
        self._children.alphaUnderrelax = Field("alphaUnderrelax", 1)
        self._children.alphaUnderrelax2 = Field("alphaUnderrelax2", 10)
        self._children.timeImpl1 = Field("timeImpl1", 1)
        self._children.timeImpl2 = Field("timeImpl1", 2)

        self._children.strucSolverMaxiter = Field("strucSolverMaxiter", 2500)
        self._children.strucSolverMaxres = Field("strucSolverMaxres", 1e-6)
        self._children.overrelax = Field("overrelax", 1)
        self._children.substepIter = Field("substepIter", 10)

        self._children.forceWeight = Field("forceWeight", 1)
        self._children.SSMForceProbeL = Field("SSMForceProbeL", 0.5)
        self._children.bendingModel = Field(
            "bendingModel", "fedkiw", "", {"fedkiw": 1, "marco": 2}
        )

        self._children.youngsModulusOpt = Field(
            "youngsModulusOpt", "const", "", {"const": 1, "variable": 2}
        )
        self._children.fibres = Field("fibres", 0, "not available now")

        self._finalize_init()

    def write(self):
        self._formatter += self._children.coupling
        self._formatter += self._children.implMaxres
        self._formatter += self._children.implMaxiter
        self._formatter.write()

        self._formatter += self._children.alpOpt
        self._formatter += self._children.alphaUnderrelax
        self._formatter += self._children.alphaUnderrelax2
        self._formatter += self._children.timeImpl1
        self._formatter += self._children.timeImpl2
        self._formatter.write()

        self._formatter += self._children.strucSolverMaxiter
        self._formatter += self._children.strucSolverMaxres
        self._formatter += self._children.overrelax
        self._formatter += self._children.substepIter
        self._formatter.write()

        self._formatter += self._children.forceWeight
        self._formatter += self._children.SSMForceProbeL
        self._formatter += self._children.bendingModel
        self._formatter.write()

        self._formatter += self._children.youngsModulusOpt
        self._formatter += self._children.fibres
        self._formatter.write()
