import shutil
from pathlib import Path
from pyvicar._tree import Group
from pyvicar.file import Readable
from pyvicar._utilities import Optional


class RestartPackPool(Group, Readable, Optional):
    def __init__(self, case, prefix):
        Group.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._case = case
        self._prefix = prefix

        self._children.t1 = RestartPack(self._case, prefix, 1)
        self._children.t2 = RestartPack(self._case, prefix, 2)

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
            raise Exception(f"No active {self._prefix} restart pack")

        t1 = get_latest_mtime(self._children.t1.path)
        t2 = get_latest_mtime(self._children.t2.path)

        if t1 > t2:
            return self._children.t1
        else:
            return self._children.t2

    @property
    def prefix(self):
        return self._prefix


class RestartPack(Group, Readable, Optional):
    def __init__(self, case, prefix, tidx):
        Group.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._case = case
        self._prefix = prefix
        self._tidx = tidx
        self._path = None

        self._finalize_init()

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    def read(self):
        rdir = self._case.path / "Restart" / f"{self._prefix}" / f"out.{self._tidx}"
        if rdir.is_dir():
            self._enable()

        self._path = rdir

    @property
    def tidx(self):
        return self._tidx

    @property
    def prefix(self):
        return self._prefix

    @property
    def path(self):
        return self._path

    def __repr__(self):
        return f"RestartPack({self._prefix}[{self._tidx}])"

    def to_restart_in(self):
        if not self:
            raise Exception(f"{self} does not exist")

        dst = self._path.parent / f"in"

        if dst.exists():
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()

        shutil.copytree(self._path, dst)


def get_latest_mtime(path):
    p = Path(path)
    if not p.exists():
        return 0

    if p.is_file():
        return p.stat().st_mtime

    files = [f for f in p.iterdir() if f.is_file()]
    if files:
        return max(f.stat().st_mtime for f in files)
    else:
        return p.stat().st_mtime
