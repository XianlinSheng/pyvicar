from pyvicar.tree.group import Group
from pyvicar.file.io import Writable
from pyvicar.tree.field import Field
from pyvicar.file.formatter import KV2Formatter

class InternalBoundary(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.internalBoundaryPresent = Field('internalBoundaryPresent', False, '', Field.vmapPresets.bool2int)
        self._children.iblankFastOptions = Field('iblankFastOptions', 'x', '', {'x': 1, 'y': 2, 'z': 3})

        self._children.icc = Field('icc', False, 'Cut Cell', Field.vmapPresets.bool2int)
        self._children.momentumCutCell = Field('momentumCutCell', False, '', Field.vmapPresets.bool2int)
        self._children.iMergeType = Field('iMergeType', False, '', Field.vmapPresets.bool2int)

        self._children.bodyType = Field('bodyType', 'canonical', '', {'general': 1, 'canonical': 2})

        self._children.boundaryFormulation = Field('boundaryFormulation', 'gcm', '', {'ssm': 1, 'gcm': 2})
        self._children.iSSMP = Field('iSSMP', False, '', Field.vmapPresets.bool2int)

        self._children.probeLengthNormalized = Field('probeLengthNormalized', 2.0)
        self._children.membCoronaSize = Field('membCoronaSize', 1)
        self._children.nElemCheckBI = Field('nElemCheckBI', 3)
        self._children.nCheckIBlank = Field('nCheckIBlank', 3)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.internalBoundaryPresent
        self._formatter += self._children.iblankFastOptions
        self._formatter.write()

        self._formatter += self._children.icc
        self._formatter += self._children.momentumCutCell
        self._formatter += self._children.iMergeType
        self._formatter.write()

        self._formatter += self._children.bodyType
        self._formatter.write()

        self._formatter += self._children.boundaryFormulation
        self._formatter += self._children.iSSMP
        self._formatter.write()

        self._formatter += self._children.probeLengthNormalized
        self._formatter += self._children.membCoronaSize
        self._formatter += self._children.nElemCheckBI
        self._formatter += self._children.nCheckIBlank
        self._formatter.write()
