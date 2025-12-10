from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter


class ComputationalDomainConfiguration(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.nRead = Field(
            "nRead", False, "read restart file", Field.vmapPresets.bool2int
        )
        self._children.flowOn = Field("flowOn", True, "", Field.vmapPresets.bool2int)
        self._children.userWallVel = Field(
            "userWallVel", False, "", Field.vmapPresets.bool2int
        )

        self._children.nDim = Field("nDim", 3)
        self._children.flowType = Field(
            "flowType", 1, "", {"viscous": 1, "potential": 2, "motionCheck": 3}
        )

        self._children.nx = Field("nx", 151)
        self._children.ny = Field("ny", 101)
        self._children.nz = Field("nz", 51)

        self._children.xgridUnif = Field(
            "xgridUnif", "uniform", "", {"uniform": 1, "nonuniform": 2}
        )
        self._children.xout = Field("xout", 15.0)

        self._children.ygridUnif = Field(
            "ygridUnif", "uniform", "", {"uniform": 1, "nonuniform": 2}
        )
        self._children.yout = Field("yout", 10.0)

        self._children.zgridUnif = Field(
            "zgridUnif", "uniform", "", {"uniform": 1, "nonuniform": 2}
        )
        self._children.zout = Field("zout", 5.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.nRead
        self._formatter += self._children.flowOn
        self._formatter += self._children.userWallVel
        self._formatter.write()

        self._formatter += self._children.nDim
        self._formatter += self._children.flowType
        self._formatter.write()

        self._formatter += self._children.nx
        self._formatter += self._children.ny
        self._formatter += self._children.nz
        self._formatter.write()

        self._formatter += self._children.xgridUnif
        self._formatter += self._children.xout
        self._formatter.write()

        self._formatter += self._children.ygridUnif
        self._formatter += self._children.yout
        self._formatter.write()

        self._formatter += self._children.zgridUnif
        self._formatter += self._children.zout
        self._formatter.write()
