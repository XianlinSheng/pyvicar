from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter


class Misc(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.fr = Field("fr", 1.0)
        self._children.stopTime = Field("stopTime", 9e99)

        self._children.nonInertial = Field(
            "nonInertial", False, "", Field.vmapPresets.bool2int
        )
        self._children.iVerbose = Field(
            "iVerbose", False, "", Field.vmapPresets.bool2int
        )

        self._children.idMemb = Field("idMemb", False, "", Field.vmapPresets.bool2int)
        self._children.iSubMG = Field("iSubMG", False, "", Field.vmapPresets.bool2int)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.fr
        self._formatter += self._children.stopTime
        self._formatter.write()

        self._formatter += self._children.nonInertial
        self._formatter += self._children.iVerbose
        self._formatter.write()

        self._formatter += self._children.idMemb
        self._formatter += self._children.iSubMG
        self._formatter.write()
