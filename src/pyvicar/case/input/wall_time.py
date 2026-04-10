from pyvicar._tree import Group, Field
from pyvicar.file import Writable
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

        self._children.iScalar = Field("iScalar", False, "", Field.vmapPresets.bool2int)

        self._children.iFullQ = Field("iFullQ", False, "", Field.vmapPresets.bool2int)
        self._children.nDimFullQ = Field("nDimFullQ", 3)
        self._children.stackSize = Field("stackSize", 100)
        self._children.stackStart = Field("stackStart", 0)
        self._children.markerFullQ = Field(
            "markerFullQ", False, "", Field.vmapPresets.bool2int
        )

        self._children.iPart = Field("iPart", False, "", Field.vmapPresets.bool2int)
        self._children.iFPM = Field(
            "iFPM", "off", "", {"off": 0, "x": 1, "y": 2, "z": 3, "power": 4}
        )
        self._children.iBodyFPM = Field("iBodyFPM", 0)
        self._children.resMaxPhi = Field("resMaxPhi", 1e-4)
        self._children.iVor = Field(
            "iVor",
            1,
            "",
            {
                "-adv dot grad(phi)": 0,
                "-2*rho*vorq": 1,
                "div(adv)*phi neumann bc": 2,
                "div(adv)*phi neumann bc 1st upwind": 3,
            },
        )

        self._finalize_init()

    def write(self):
        self._formatter += self._children.systemWallTime
        self._formatter += self._children.exitSafeTime
        self._formatter += self._children.iSafeTime
        self._formatter.write()

        self._formatter += self._children.iScalar
        self._formatter.write()

        self._formatter += self._children.iFullQ
        self._formatter += self._children.nDimFullQ
        self._formatter += self._children.stackSize
        self._formatter += self._children.stackStart
        self._formatter += self._children.markerFullQ
        self._formatter.write()

        self._formatter += self._children.iPart
        self._formatter += self._children.iFPM
        self._formatter += self._children.iBodyFPM
        self._formatter += self._children.resMaxPhi
        self._formatter += self._children.iVor
        self._formatter.write()
