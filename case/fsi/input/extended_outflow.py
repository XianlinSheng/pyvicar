from pyvicar.tree.group import Group
from pyvicar.file.io import Writable
from pyvicar.tree.field import Field
from pyvicar.file.formatter import KV2Formatter

class ExtendedOutflow(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.extendedOutFlow = Field('extendedOutflow', False, '', Field.vmapPresets.bool2int)
        self._children.xext = Field('xext', 2.0)
        self._children.dampingFactor = Field('dampingFactor', 5.0)

        self._finalize_init()


    def write(self):
        self._formatter += self._children.extendedOutFlow
        self._formatter += self._children.xext
        self._formatter += self._children.dampingFactor
        self._formatter.write()


