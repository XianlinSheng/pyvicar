import numpy as np
from pathlib import Path
from pyvicar._utilities.optional import Optional
from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV1Formatter, DatasetFormatter
import pyvicar.tools.srj as srj
import pyvicar.tools.log as log


class SRJ(Group, Writable, Optional):
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

        self._finalize_init()

    def enable(self):
        Optional.enable(self)
        self._init()

    def write(self):
        if not self:
            raise Exception(f"SRJ is not active, call .enable() to enable it")

        self._headerFormatter += self._children.nomega
        self._headerFormatter.write()

        self._arrayFormatter += self._children.omegas
        self._arrayFormatter.write()

        self._f.flush()

    def set_params(self, key=None, gridN=None, db="./srj_db.h5", rdb="srj_rdb.h5"):
        if not self:
            raise Exception(f"SRJ is not active, call .enable() to enable it")

        if key is None:
            p = srj.preset36()
        else:
            p = read_params(key, gridN, db, rdb)

        self.nomega = p.nomega
        self.omegas = p.omegas

    def set_jacobi(self):
        self.nomega = 1
        self.omegas = np.array([[1]], dtype=float)


def read_params(key, gridN, db, rdb):
    if not Path(rdb).exists():
        if not Path(db).exists():
            log.log_host("Generating Original SRJ DB")
            srj.generate_database(db)

        log.log_host("Generating Rearranged SRJ DB")
        srj.generate_rearranged_database(db, rdb, gridN)

    return srj.read_rearranged_omegas(key, rdb)
