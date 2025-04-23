from pyvicar.tree.group import Group
from pyvicar.file.io import Writable
from pyvicar.tree.field import Field
from pyvicar.file.formatter import KV2Formatter

class OutputFormat(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.iFullQ = Field('iFullQ', False, '', Field.vmapPresets.bool2int)
        self._children.nDimFullQ = Field('nDimFullQ', 2)
        self._children.stackSize = Field('stackSize', 100)
        self._children.stackStart = Field('stackStart', 0)
        self._children.markerFullQ = Field('markerFullQ', False, '', Field.vmapPresets.bool2int)

        self._finalize_init()


    def write(self):
        self._formatter += self._children.iFullQ
        self._formatter += self._children.nDimFullQ
        self._formatter += self._children.stackSize
        self._formatter += self._children.stackStart
        self._formatter += self._children.markerFullQ
        self._formatter.write()

