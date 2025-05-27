from pyvicar._utilities import Optional
from pyvicar._tree import Group, Field
from pyvicar._file import Writable
from pyvicar._format import KV1Formatter


class RestrictedHinge(Group, Writable, Optional):
    def __init__(self, f, defaulton=False):
        Optional.__init__(self, defaulton)
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.restrictLower = Field(
            "restrictLower", False, "", Field.vmapPresets.bool2int
        )
        self._children.restrictUpper = Field(
            "restrictUpper", False, "", Field.vmapPresets.bool2int
        )

        self._children.ampangxl = Field("ampangxl", 0.0)
        self._children.ampangyl = Field("ampangyl", 0.0)
        self._children.ampangzl = Field("ampangzl", 0.0)

        self._children.freqangxl = Field("freqangxl", 0.0)
        self._children.freqangyl = Field("freqangyl", 0.0)
        self._children.freqangzl = Field("freqangzl", 0.0)

        self._children.phaseangxl = Field("phaseangxl", 0.0)
        self._children.phaseangyl = Field("phaseangyl", 0.0)
        self._children.phaseangzl = Field("phaseangzl", 0.0)

        self._children.ampangxu = Field("ampangxu", 0.0)
        self._children.ampangyu = Field("ampangyu", 0.0)
        self._children.ampangzu = Field("ampangzu", 0.0)

        self._children.freqangxu = Field("freqangxu", 0.0)
        self._children.freqangyu = Field("freqangyu", 0.0)
        self._children.freqangzu = Field("freqangzu", 0.0)

        self._children.phaseangxu = Field("phaseangxu", 0.0)
        self._children.phaseangyu = Field("phaseangyu", 0.0)
        self._children.phaseangzu = Field("phaseangzu", 0.0)

        self._children.angxinit = Field("angxinit", 0.0)
        self._children.angyinit = Field("angyinit", 0.0)
        self._children.angzinit = Field("angzinit", 0.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.restrictLower
        self._formatter += self._children.restrictUpper
        self._formatter.splittext = "|-restrictedHinge"
        self._formatter.write()
        self._formatter.splittext = " |-"

        self._formatter += self._children.ampangxl
        self._formatter += self._children.ampangyl
        self._formatter += self._children.ampangzl
        self._formatter.write()

        self._formatter += self._children.freqangxl
        self._formatter += self._children.freqangyl
        self._formatter += self._children.freqangzl
        self._formatter.write()

        self._formatter += self._children.phaseangxl
        self._formatter += self._children.phaseangyl
        self._formatter += self._children.phaseangzl
        self._formatter.write()

        self._formatter += self._children.ampangxu
        self._formatter += self._children.ampangyu
        self._formatter += self._children.ampangzu
        self._formatter.write()

        self._formatter += self._children.freqangxu
        self._formatter += self._children.freqangyu
        self._formatter += self._children.freqangzu
        self._formatter.write()

        self._formatter += self._children.phaseangxu
        self._formatter += self._children.phaseangyu
        self._formatter += self._children.phaseangzu
        self._formatter.write()

        self._formatter += self._children.angxinit
        self._formatter += self._children.angyinit
        self._formatter += self._children.angzinit
        self._formatter.write()
