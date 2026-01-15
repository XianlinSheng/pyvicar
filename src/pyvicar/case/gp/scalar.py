from pathlib import Path
from pyvicar._tree import Group, List, Field
from pyvicar._utilities import Optional
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter, write_banner
from pyvicar.tools.physics_setter.common import set_scalar_inlet


class Scalar(Group, Writable, Optional):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)
        Optional.__init__(self)
        self._path = Path(path)
        if self:
            self._init()

    def _init(self):
        self._f = open(self._path, "w")
        self._headerFormatter = KV2Formatter(self._f)

        self._children.nScalars = Field("nScalars", 0)
        self._children.iRestart = Field(
            "iRestart", False, "", Field.vmapPresets.bool2int
        )
        self._children.reactionType = Field(
            "reactionType", "none", "", {"none": 0, "thrombosis": 10, "user": 20}
        )

        self._children.discreteType = Field(
            "discreteType",
            "conservative",
            "consv. d(uT); nconsv. udT",
            {"conservative": 1, "non_conservative": 1},
        )
        self._children.upwindw = Field("upwindw", 1.0)
        self._children.solverType = Field(
            "solverType", "iterative", "", {"iterative": 0, "rk4": 1}
        )

        self._children.tmin = Field("tmin", -1e20, "cutoff min")
        self._children.tmax = Field("tmax", 1e20, "cutoff max")

        self._children.vars = ScalarVars(self._f)

        self._finalize_init()

    def enable(self):
        Optional.enable(self)
        self._init()

    def write(self):
        if not self:
            raise Exception(f"The object is not active, call .enable() to enable it")

        f = self._f

        write_banner(f, "General Configuration")

        self._headerFormatter += self._children.nScalars
        self._headerFormatter += self._children.iRestart
        self._headerFormatter += self._children.reactionType
        self._headerFormatter.write()

        self._headerFormatter += self._children.discreteType
        self._headerFormatter += self._children.upwindw
        self._headerFormatter += self._children.solverType
        self._headerFormatter.write()

        self._headerFormatter += self._children.tmin
        self._headerFormatter += self._children.tmax
        self._headerFormatter.write()

        write_banner(f, "Variable Configuration (vars)")
        self._children.vars.write()

        f.flush()


class ScalarVars(List, Writable):
    def __init__(self, f):
        List.__init__(self)
        Writable.__init__(self)
        self._f = f

    def _elemcheck(self, new):
        if not isinstance(new, ScalarVar):
            raise TypeError(
                f"Expected an ScalarVar object, but encountered {repr(new)}"
            )

    def write(self):
        f = self._f

        for i, var in enumerate(self):
            write_banner(f, f"Variable T{i+1}", filler="-")
            var.write()

    def appendnew(self, n=1):
        newobjs = [ScalarVar(self._f) for _ in range(n)]
        self._childrenlist += newobjs
        if n == 1:
            return newobjs[0]
        else:
            return newobjs

    def resetnew(self, n=1):
        self._childrenlist = [ScalarVar(self._f) for _ in range(n)]


dbcmap = {"dirichlet": 1, "neumann": 2, "user": 20}
ibcmap = {"adiabatic": 0, "isothermal": 1, "distribution": 2}
icmap = {"uniform": 0, "box_uniform": 1, "data_array": 2}


class ScalarVar(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.bcx1 = Field("bcx1", "neumann", "", dbcmap)
        self._children.tbcx1 = Field("tbcx1", 0.0)
        self._children.bcx2 = Field("bcx2", "neumann", "", dbcmap)
        self._children.tbcx2 = Field("tbcx2", 0.0)

        self._children.bcy1 = Field("bcy1", "neumann", "", dbcmap)
        self._children.tbcy1 = Field("tbcy1", 0.0)
        self._children.bcy2 = Field("bcy2", "neumann", "", dbcmap)
        self._children.tbcy2 = Field("tbcy2", 0.0)

        self._children.bcz1 = Field("bcz1", "neumann", "", dbcmap)
        self._children.tbcz1 = Field("tbcz1", 0.0)
        self._children.bcz2 = Field("bcz2", "neumann", "", dbcmap)
        self._children.tbcz2 = Field("tbcz2", 0.0)

        self._children.sc = Field("sc", 1e3)
        self._children.iadvec = Field("iadvec", True, "", Field.vmapPresets.bool2int)
        self._children.idiff = Field("idiff", True, "", Field.vmapPresets.bool2int)

        self._children.icType = Field("icType", "uniform", "", icmap)
        self._children.icVal = Field("icVal", 0.0)

        self._children.innerbcType = Field("innerbcType", "adiabatic", "", ibcmap)
        self._children.innerbcVal = Field("innerbcVal", 0.0)
        self._children.iUserSrc = Field(
            "iUserSrc", False, "", Field.vmapPresets.bool2int
        )

        self._finalize_init()

    def write(self):
        self._formatter += self._children.bcx1
        self._formatter += self._children.tbcx1
        self._formatter.write()

        self._formatter += self._children.bcx2
        self._formatter += self._children.tbcx2
        self._formatter.write()

        self._formatter += self._children.bcy1
        self._formatter += self._children.tbcy1
        self._formatter.write()

        self._formatter += self._children.bcy2
        self._formatter += self._children.tbcy2
        self._formatter.write()

        self._formatter += self._children.bcz1
        self._formatter += self._children.tbcz1
        self._formatter.write()

        self._formatter += self._children.bcz2
        self._formatter += self._children.tbcz2
        self._formatter.write()

        self._formatter += self._children.sc
        self._formatter += self._children.iadvec
        self._formatter += self._children.idiff
        self._formatter.write()

        self._formatter += self._children.icType
        self._formatter += self._children.icVal
        self._formatter.write()

        self._formatter += self._children.innerbcType
        self._formatter += self._children.innerbcVal
        self._formatter += self._children.iUserSrc
        self._formatter.write()


ScalarVar.set_inlet = set_scalar_inlet
