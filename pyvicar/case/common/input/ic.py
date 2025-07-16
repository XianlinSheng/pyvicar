from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter


class InitialConditions(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

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
        self._formatter += self._children.uinit
        self._formatter += self._children.vinit
        self._formatter += self._children.winit
        self._formatter += self._children.perturbation
        self._formatter += self._children.fullyDevelopedProfile
        self._formatter += self._children.ICIn
        self._formatter.write()
