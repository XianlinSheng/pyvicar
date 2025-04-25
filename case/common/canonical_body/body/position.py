from pyvicar._tree import Group, Field
from pyvicar._file import Writable
from pyvicar._format import KV1Formatter


class Position(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.radiusx = Field("radiusx", 0.0)
        self._children.radiusy = Field("radiusy", 0.0)
        self._children.radiusz = Field("radiusz", 0.0)

        self._children.centx = Field("centx", 0.0)
        self._children.centy = Field("centy", 0.0)
        self._children.centz = Field("centz", 0.0)

        self._children.alpha = Field("alpha", 0.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.radiusx
        self._formatter += self._children.radiusy
        self._formatter += self._children.radiusz
        self._formatter.splittext = "|-position"
        self._formatter.write()
        self._formatter.splittext = " |-"

        self._formatter += self._children.centx
        self._formatter += self._children.centy
        self._formatter += self._children.centz
        self._formatter.write()

        self._formatter += self._children.alpha
        self._formatter.write()
