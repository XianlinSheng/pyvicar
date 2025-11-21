from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV1Formatter


class General(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.bodyType = Field("body_type", "unstruc", "", {"unstruc": 4})
        self._children.bodyDim = Field("body_dim", 3)
        self._children.motionType = Field(
            "motionType",
            "stationary",
            "",
            {
                "stationary": 0,
                "forced": 1,
                "flow_induced": 2,
                "prescribed": 3,
                "hinged": 4,
                "rhm": 15,
                "ib2": 16,
            },
        )
        self._children.membraneType = Field(
            "membraneType", "open", "", {"open": 1, "closed": 2, "diff": 3}
        )

        self._children.combinedType = Field("combinedType", 0)
        self._children.combinedGroupIndex = Field("combinedGroupIndex", 0)
        self._children.surfaceIntegral = Field(
            "surfaceIntegral", True, "", Field.vmapPresets.bool2int
        )

        self._children.wallType = Field(
            "wallType",
            "noslip_nonporous",
            "",
            {"noslip_nonporous": 0, "slip_porous": 1},
        )

        self._children.nPtsGCMBodyMarker = Field("nPtsGCMBodyMarker", 0)
        self._children.nTriElement = Field("nTriElement", 0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.bodyType
        self._formatter += self._children.bodyDim
        self._formatter += self._children.motionType
        self._formatter += self._children.membraneType
        self._formatter.splittext = "|-general"
        self._formatter.write()
        self._formatter.splittext = " |-"

        self._formatter += self._children.combinedType
        self._formatter += self._children.combinedGroupIndex
        self._formatter += self._children.surfaceIntegral
        self._formatter.write()

        self._formatter += self._children.wallType
        self._formatter.write()

        self._formatter += self._children.nPtsGCMBodyMarker
        self._formatter += self._children.nTriElement
        self._formatter.write()
