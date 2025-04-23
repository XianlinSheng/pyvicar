import numpy as np
from pathlib import Path
from pyvicar.utilities import Optional
from pyvicar.tree.group import Group
from pyvicar.tree.field import Field
from pyvicar.file.io import Writable
from pyvicar.file.formatter import DatasetFormatter


class NonuniformGrid(Group, Writable, Optional):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)
        Optional.__init__(self)
        self._path = Path(path)
        if self:
            self._init()


    def _init(self):
        self._f = open(self._path, 'w')
        self._formatter = DatasetFormatter(self._f)
        self._formatter.printidx = True

        self._children.nodes = Field('nodes', np.zeros((0, 1), dtype=float))

        self._finalize_init()


    def enable(self):
        Optional.enable(self)
        self._init()


    def write(self):
        if not self:
            raise Exception(f'The object is not active, call .enable() to enable it')

        self._formatter += self._children.nodes
        self._formatter.write()

