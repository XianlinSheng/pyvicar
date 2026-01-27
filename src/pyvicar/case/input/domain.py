from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter


class ComputationalDomainConfiguration(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.iRestart = Field(
            "iRestart", False, "", Field.vmapPresets.bool2int
        )
        self._children.iAcou = Field("iAcou", False, "", Field.vmapPresets.bool2int)
        self._children.nsa = Field("nsa", 4)
        self._children.iAcouRest = Field(
            "iAcouRest", False, "", Field.vmapPresets.bool2int
        )
        self._children.iFlow = Field("iFlow", True, "", Field.vmapPresets.bool2int)
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

        self._children.uinit = Field("uinit", 0.0)
        self._children.vinit = Field("vinit", 0.0)
        self._children.winit = Field("winit", 0.0)
        self._children.perturbation = Field("perturbation", 0.0)
        self._children.fullyDevelopedProfile = Field(
            "fullyDevelopedProfile", False, "", Field.vmapPresets.bool2int
        )
        self._children.ICIn = Field("ICIn", False, "", Field.vmapPresets.bool2int)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.iRestart
        self._formatter += self._children.iAcou
        self._formatter += self._children.nsa
        self._formatter += self._children.iAcouRest
        self._formatter += self._children.iFlow
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

        self._formatter += self._children.uinit
        self._formatter += self._children.vinit
        self._formatter += self._children.winit
        self._formatter += self._children.perturbation
        self._formatter += self._children.fullyDevelopedProfile
        self._formatter += self._children.ICIn
        self._formatter.write()
