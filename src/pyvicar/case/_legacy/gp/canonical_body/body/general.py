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
            },
        )
        self._children.membraneType = Field(
            "membraneType", "open", "", {"open": 1, "closed": 2, "diff": 3}
        )

        self._children.wallType = Field(
            "wallType",
            "noslip_nonporous",
            "",
            {"noslip_nonporous": 0, "slip_porous": 1},
        )
        self._children.velTemporalType = Field(
            "velTemporalType",
            "const",
            "",
            {
                "const": 0,
                "alternate_cos": 1,
                "positive_cos": 2,
                "amplitude_list": 3,
                "user": 20,
            },
        )
        self._children.velSpatialType = Field(
            "velSpatialType",
            "uniform",
            "",
            {"uniform": 0, "normal_uniform": 1, "data_array": 2, "user": 20},
        )

        self._children.nPoint = Field("nPoint", 0)
        self._children.nElem = Field("nElem", 0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.bodyType
        self._formatter += self._children.bodyDim
        self._formatter += self._children.motionType
        self._formatter += self._children.membraneType
        self._formatter.splittext = "|-general"
        self._formatter.write()
        self._formatter.splittext = " |-"

        self._formatter += self._children.wallType
        self._formatter += self._children.velTemporalType
        self._formatter += self._children.velSpatialType
        self._formatter.write()

        self._formatter += self._children.nPoint
        self._formatter += self._children.nElem
        self._formatter.write()
