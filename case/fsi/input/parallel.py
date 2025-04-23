from pyvicar.tree.group import Group
from pyvicar.file.io import Writable
from pyvicar.tree.field import Field
from pyvicar.file.formatter import KV2Formatter


class ParallelConfiguration(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.npx = Field('npx', 2, 'n processes in x')
        self._children.npy = Field('npy', 2, 'n processes in y')

        self._children.ngl = Field('ngl', 2, 'ghost layer thickness')

        self._finalize_init()


    def write(self):
        self._formatter += self._children.npx
        self._formatter += self._children.npy
        self._formatter.write()

        self._formatter += self._children.ngl
        self._formatter.write()

