from pyvicar.tree.group import Group
from pyvicar.file.io import Writable
from pyvicar.tree.field import Field
from pyvicar.file.formatter import KV2Formatter

class Scalars(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.scalarOn = Field('scalarOn', False, '', Field.vmapPresets.bool2int)
        self._children.iPart = Field('iPart', False, '', Field.vmapPresets.bool2int)
        self._children.iDisDelta = Field('iDisDelta', False, '', Field.vmapPresets.bool2int)

        self._finalize_init()


    def write(self):
        self._formatter += self._children.scalarOn
        self._formatter += self._children.iPart
        self._formatter += self._children.iDisDelta
        self._formatter.write()

