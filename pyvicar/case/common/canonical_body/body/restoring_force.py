from pyvicar._tree import Group, Field
from pyvicar._file import Writable
from pyvicar._format import KV1Formatter


class RestoringForce(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.xcentConstR = Field("xcentConstR", 0.0)
        self._children.ycentConstR = Field("ycentConstR", 0.0)
        self._children.zcentConstR = Field("zcentConstR", 0.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.xcentConstR
        self._formatter += self._children.ycentConstR
        self._formatter += self._children.zcentConstR
        self._formatter.splittext = "|-restrForce"
        self._formatter.write()
        self._formatter.splittext = " |-"
