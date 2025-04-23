from pyvicar.tree.group import Group
from pyvicar.file.io import Writable
from pyvicar.tree.field import Field
from pyvicar.file.formatter import KV2Formatter

class Acoustics(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.iacou = Field('iacou', False, '', Field.vmapPresets.bool2int)
        self._children.nsa = Field('nsa', 4)
        self._children.iacouRest = Field('iacouRest', True, '', Field.vmapPresets.bool2int)

        self._finalize_init()


    def write(self):
        self._formatter += self._children.iacou
        self._formatter += self._children.nsa
        self._formatter += self._children.iacouRest
        self._formatter.write()
