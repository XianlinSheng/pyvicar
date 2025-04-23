import numpy as np
from pyvicar.tree.group import Group
from pyvicar.file.io import Writable
from pyvicar.tree.field import Field
from pyvicar.file.formatter import KV1Formatter, DatasetFormatter


class Markers(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._headerFormatter = KV1Formatter(f)
        self._arrayFormatter = DatasetFormatter(f)

        self._children.nProbeMarker = Field('nProbeMarker', 0)
        self._children.bimi = Field('bimi', np.zeros((0, 2)), 'bodyi markeri')

        self._finalize_init()


    def write(self, **kwargs):
        self._headerFormatter += self._children.nProbeMarker
        self._headerFormatter.write()
        self._arrayFormatter += self._children.bimi
        self._arrayFormatter.write()

