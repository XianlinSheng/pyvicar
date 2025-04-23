from pyvicar.tree.group import Group
from pyvicar.file.io import Writable
from pyvicar.tree.field import Field
from pyvicar.file.formatter import KV2Formatter

class FEA(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.iflux = Field('iflux', 0)
        self._children.jflux = Field('jflux', 0)
        self._children.kflux = Field('kflux', 0)

        self._finalize_init()


    def write(self):
        self._formatter += self._children.iflux
        self._formatter += self._children.jflux
        self._formatter += self._children.kflux
        self._formatter.write()

