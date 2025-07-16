import shutil
from pyvicar._tree import Group
from pyvicar.file import Readable
from pyvicar._utilities import Optional


class FIMList(Group, Readable, Optional):
    def __init__(self, case):
        Group.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._case = case

        self._children.t1 = FIM(self._case, 1)
        self._children.t2 = FIM(self._case, 2)

        self._finalize_init()

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    def read(self):
        self._children.t1.read()
        self._children.t2.read()

        if self._children.t1 or self._children.t2:
            self._enable()

    @property
    def latest(self):
        if not self:
            raise Exception(f"No active restart fim out files")

        if self._children.t1:
            t1 = self._children.t1.path.stat().st_mtime
        else:
            t1 = 0

        if self._children.t2:
            t2 = self._children.t2.path.stat().st_mtime
        else:
            t2 = 0

        if t1 > t2:
            return self._children.t1
        else:
            return self._children.t2


class FIM(Group, Readable, Optional):
    def __init__(self, case, tidx):
        Group.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)

        self._case = case
        self._path = None
        self._tidx = tidx

    def read(self):
        filepath = self._case.path / "Restart" / f"restart_fim_out.{self._tidx}.dat"

        if filepath.exists():
            self._path = filepath
            self._enable()

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    @property
    def path(self):
        return self._path

    @property
    def tidx(self):
        return self._tidx

    def to_restart_in(self):
        if not self:
            raise Exception(f"No active restart fim out file")

        newpath = self._case.path / "Restart" / f"restart_fim_in.dat"
        shutil.copy(self._path, newpath)
        return newpath

    def __repr__(self):
        return f"RestartFIM(tidx = {self._tidx})"
