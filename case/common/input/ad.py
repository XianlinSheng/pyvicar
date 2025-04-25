from pyvicar._tree import Group, Field
from pyvicar._file import Writable
from pyvicar._format import KV2Formatter


class AdvectionDiffusionSolver(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.itermax = Field("itermax", 1000)
        self._children.resmax = Field("resmax", 1e-10)
        self._children.omegaAdv = Field("omegaAdv", 1.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.itermax
        self._formatter += self._children.resmax
        self._formatter += self._children.omegaAdv
        self._formatter.write()
