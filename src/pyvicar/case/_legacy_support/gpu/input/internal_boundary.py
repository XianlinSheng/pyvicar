from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter


class InternalBoundary(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.iib = Field("iib", False, "", Field.vmapPresets.bool2int)
        self._children.iBlank = Field(
            "iBlank", "gpu", "", {"slow": 0, "fast": 1, "gpu": 4}
        )
        self._children.iCC = Field("iCC", False, "Cut Cell", Field.vmapPresets.bool2int)
        self._children.iSSMP = Field("iSSMP", False, "", Field.vmapPresets.bool2int)
        self._children.iMergeType = Field(
            "iMergeType", False, "", Field.vmapPresets.bool2int
        )

        self._children.bodyType = Field(
            "bodyType", "canonical", "", {"general": 1, "canonical": 2}
        )
        self._children.membCoronaSize = Field("membCoronaSize", 1)
        self._children.nCheckBI = Field("nCheckBI", 3)
        self._children.nCheckIBlank = Field("nCheckIBlank", 3)

        self._children.form = Field("form", "gcm", "", {"ssm": 1, "gcm": 2})
        self._children.extOutflow = Field(
            "extOutflow", False, "", Field.vmapPresets.bool2int
        )
        self._children.xext = Field("xext", 0.0)
        self._children.dampFactor = Field("dampFactor", 0.0)

        self._children.probeLen = Field("probeLen", 2.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.iib
        self._formatter += self._children.iBlank
        self._formatter += self._children.iCC
        self._formatter += self._children.iSSMP
        self._formatter += self._children.iMergeType
        self._formatter.write()

        self._formatter += self._children.bodyType
        self._formatter += self._children.membCoronaSize
        self._formatter += self._children.nCheckBI
        self._formatter += self._children.nCheckIBlank
        self._formatter.write()

        self._formatter += self._children.form
        self._formatter += self._children.extOutflow
        self._formatter += self._children.xext
        self._formatter += self._children.dampFactor
        self._formatter.write()

        self._formatter += self._children.probeLen
        self._formatter.write()
