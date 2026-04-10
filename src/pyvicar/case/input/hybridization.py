from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter


class Hybridization(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.upwindWeight = Field(
            "upwindWeight",
            "upwind",
            "",
            {"central": 0.0, "upwind": 1.0, "quick": 0.875},
        )
        self._children.iDirectForcing = Field(
            "iDirectforcing", False, "", Field.vmapPresets.bool2int
        )

        self._finalize_init()

    def write(self):
        self._formatter += self._children.upwindWeight
        self._formatter += self._children.iDirectForcing
        self._formatter.write()
