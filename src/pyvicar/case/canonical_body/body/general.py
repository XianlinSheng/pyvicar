from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV1Formatter
from pyvicar.tools.miscellaneous import args


class General(Group, Writable):
    def __init__(self, f, config):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        config = args.add_default(
            config,
            {
                "body_types": {
                    "default": "unstruc",
                    "vmap": {
                        "unstruc": 4,
                    },
                },
                "motion_types": {
                    "default": "stationary",
                    "vmap": {
                        "stationary": 0,
                        "forced": 1,
                        "flow_induced": 2,
                        "prescribed": 3,
                    },
                },
                "membrane_types": {
                    "default": "open",
                    "vmap": {"open": 1, "closed": 2, "diff": 3},
                },
                "wall_types": {
                    "default": "noslip_nonporous",
                    "vmap": {"noslip_nonporous": 0, "slip_porous": 1},
                },
            },
            recursive=True,
        )

        self._children.bodyType = Field(
            "body_type",
            config["body_types"]["default"],
            "",
            config["body_types"]["vmap"],
        )
        self._children.bodyDim = Field("body_dim", 3)
        self._children.motionType = Field(
            "motionType",
            config["motion_types"]["default"],
            "",
            config["motion_types"]["vmap"],
        )
        self._children.membraneType = Field(
            "membraneType",
            config["membrane_types"]["default"],
            "",
            config["membrane_types"]["vmap"],
        )

        self._children.wallType = Field(
            "wallType",
            config["wall_types"]["default"],
            "",
            config["wall_types"]["vmap"],
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
        self._formatter.write()

        self._formatter += self._children.nPoint
        self._formatter += self._children.nElem
        self._formatter.write()
