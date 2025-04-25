import numpy as np
from pathlib import Path
from pyvicar._utilities.optional import Optional
from pyvicar._tree import Group, Field
from pyvicar._file import Writable
from pyvicar._format import DatasetFormatter


class NonuniformGrid(Group, Writable, Optional):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)
        Optional.__init__(self)
        self._path = Path(path)
        if self:
            self._init()

    def _init(self):
        self._f = open(self._path, "w")
        self._formatter = DatasetFormatter(self._f)
        self._formatter.printidx = True

        self._children.nodes = Field("nodes", np.zeros((0, 1), dtype=float))

        self._finalize_init()

    def enable(self):
        Optional.enable(self)
        self._init()

    def write(self):
        if not self:
            raise Exception(f"The object is not active, call .enable() to enable it")

        self._formatter += self._children.nodes
        self._formatter.write()
