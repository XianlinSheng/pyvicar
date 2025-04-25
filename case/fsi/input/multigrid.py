from pyvicar._tree import Group, Field
from pyvicar._file import Writable
from pyvicar._format import KV2Formatter

mgCycleType = {"vcycle": 1, "wcycle": 2, "fcycle": 3}


class MultigridMethod(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.xCycleType = Field("xCycleType", "vcycle", "", mgCycleType)
        self._children.yCycleType = Field("yCycleType", "vcycle", "", mgCycleType)
        self._children.zCycleType = Field("zCycleType", "vcycle", "", mgCycleType)

        self._children.iterFinest = Field("iterFinest", 1)
        self._children.iterInterInc = Field("iterInterInc", 0, "0 when linear increase")
        self._children.iterCoarse = Field("iterCoarse", 1)

        self._children.xChangeGridLevelN = Field(
            "xChangeGridLevelN", False, "", Field.vmapPresets.bool2int
        )
        self._children.yChangeGridLevelN = Field(
            "yChangeGridLevelN", False, "", Field.vmapPresets.bool2int
        )
        self._children.zChangeGridLevelN = Field(
            "zChangeGridLevelN", False, "", Field.vmapPresets.bool2int
        )

        self._children.outputConvergence = Field(
            "outputConvergence", False, "", Field.vmapPresets.bool2int
        )

        self._children.nCellCoarseLevel = Field("nCellCoarseLevel", 2)
        self._children.iSubMG = Field("iSubMG", False, "", Field.vmapPresets.bool2int)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.xCycleType
        self._formatter += self._children.yCycleType
        self._formatter += self._children.zCycleType
        self._formatter.write()

        self._formatter += self._children.iterFinest
        self._formatter += self._children.iterInterInc
        self._formatter += self._children.iterCoarse
        self._formatter.write()

        self._formatter += self._children.xChangeGridLevelN
        self._formatter += self._children.yChangeGridLevelN
        self._formatter += self._children.zChangeGridLevelN
        self._formatter.write()

        self._formatter += self._children.outputConvergence
        self._formatter.write()

        self._formatter += self._children.nCellCoarseLevel
        self._formatter += self._children.iSubMG
        self._formatter.write()
