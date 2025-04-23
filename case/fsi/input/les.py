from pyvicar.tree.group import Group
from pyvicar.file.io import Writable
from pyvicar.tree.field import Field
from pyvicar.file.formatter import KV2Formatter

class LES(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.turbActive = Field('turbActive', False, '', Field.vmapPresets.bool2int)

        self._children.turbModel = Field('turbModel', 3, '', {'dynsmag': 1, 'dynlagr': 2})

        self._children.cSmagFix = Field('cSmagFix', 'turbulent', 'for dynlagr init', {'laminar': 0.0, 'turbulent': 0.1})

        self._children.xTestFilter = Field('xTestFilter', True, '', Field.vmapPresets.bool2int)
        self._children.yTestFilter = Field('yTestFilter', True, '', Field.vmapPresets.bool2int)
        self._children.zTestFilter = Field('zTestFilter', True, '', Field.vmapPresets.bool2int)

        self._children.xFilterWidthRatio = Field('xFilterWidthRatio', 2.0)
        self._children.yFilterWidthRatio = Field('yFilterWidthRatio', 2.0)
        self._children.zFilterWidthRatio = Field('zFilterWidthRatio', 2.0)

        self._children.turbulentChannel = Field('turbulentChannel', False, '', Field.vmapPresets.bool2int)
        self._children.fnx = Field('fnx', 32)
        self._children.fnz = Field('fnz', 32)
        self._children.noise = Field('noise', 5.0)

        self._finalize_init()


    def write(self):
        self._formatter += self._children.turbActive
        self._formatter.write()

        self._formatter += self._children.turbModel
        self._formatter.write()

        self._formatter += self._children.cSmagFix
        self._formatter.write()

        self._formatter += self._children.xTestFilter
        self._formatter += self._children.yTestFilter
        self._formatter += self._children.zTestFilter
        self._formatter.write()

        self._formatter += self._children.xFilterWidthRatio
        self._formatter += self._children.yFilterWidthRatio
        self._formatter += self._children.zFilterWidthRatio
        self._formatter.write()

        self._formatter += self._children.turbulentChannel
        self._formatter += self._children.fnx
        self._formatter += self._children.fnz
        self._formatter += self._children.noise
        self._formatter.write()

