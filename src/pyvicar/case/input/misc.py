from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter


class Misc(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.iMisc = Field(
            "iMisc",
            False,
            "when seeing this it means the Misc is a default built-in dummy group not specialized by any distribution",
            Field.vmapPresets.bool2int,
        )

        self._finalize_init()

    def write(self):
        self._formatter += self._children.iMisc
        self._formatter.write()
