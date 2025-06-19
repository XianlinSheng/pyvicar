import numpy as np
from pathlib import Path
from pyvicar._utilities.optional import Optional
from pyvicar._tree import Group, Field
from pyvicar._file import Writable
from pyvicar._format import KV1Formatter, DatasetFormatter


class SRJ2(Group, Writable, Optional):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)
        Optional.__init__(self)
        self._path = Path(path)
        if self:
            self._init()

    def _init(self):
        self._f = open(self._path, "w")
        self._headerFormatter = KV1Formatter(self._f)
        self._arrayFormatter = DatasetFormatter(self._f)
        self._arrayFormatter.printidx = False

        self._children.nomega = Field("nomega", 0)
        self._children.omegas = Field("omegas", np.zeros((0, 1), dtype=float))
        self._children.nomega2 = Field("nomega2", 0)
        self._children.omegas2 = Field("omegas2", np.zeros((0, 1), dtype=float))

        self._finalize_init()

    def enable(self):
        Optional.enable(self)
        self._init()

    def write(self):
        if not self:
            raise Exception(f"The object is not active, call .enable() to enable it")

        self._headerFormatter += self._children.nomega
        self._headerFormatter.write()

        self._arrayFormatter += self._children.omegas
        self._arrayFormatter.write()

        self._headerFormatter += self._children.nomega2
        self._headerFormatter.write()

        self._arrayFormatter += self._children.omegas2
        self._arrayFormatter.write()

        self._f.flush()
