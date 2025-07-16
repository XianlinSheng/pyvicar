import shutil
from pyvicar._tree import List, Group
from pyvicar.file import Readable, Series
from pyvicar._utilities import Optional


class BodyLists(Group, Readable, Optional):
    def __init__(self, case):
        Group.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._case = case

        self._children.t1 = BodyList(self._case, 1)
        self._children.t2 = BodyList(self._case, 2)

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
            raise Exception(f"No active restart body out files")

        if self._children.t1:
            t1 = self._children.t1[0].path.stat().st_mtime
        else:
            t1 = 0

        if self._children.t2:
            t2 = self._children.t2[0].path.stat().st_mtime
        else:
            t2 = 0

        if t1 > t2:
            return self._children.t1
        else:
            return self._children.t2


class BodyList(List, Readable, Optional):
    def __init__(self, case, tidx):
        List.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._case = case
        self._tidx = tidx

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    def _elemcheck(self, new):
        if not isinstance(new, Body):
            raise TypeError(
                f"Expected a Body object inside BodyList, but encountered {repr(new)}"
            )

    def _append(self, *args, **kwargs):
        return super().append(*args, **kwargs)

    def _insert(self, *args, **kwargs):
        return super().insert(*args, **kwargs)

    def read(self):
        series = Series.from_format(
            self._case.path / "Restart",
            r"restart_body_out\.(\d{5})\." + f"{self._tidx}" + r"\.dat",
        )
        for file in series:
            body = Body(self._case, file.path, file.idxes[0], self._tidx)
            self._append(body)

        if series:
            self._enable()

    @property
    def tidx(self):
        return self._tidx

    def to_restart_in(self):
        if not self:
            raise Exception(f"No active restart body in files")

        for body in self._childrenlist:
            body.to_restart_in()


class Body:
    def __init__(self, case, path, iproc, tidx):
        self._case = case
        self._path = path
        self._iproc = iproc
        self._tidx = tidx

    @property
    def path(self):
        return self._path

    @property
    def iproc(self):
        return self._iproc

    @property
    def tidx(self):
        return self._tidx

    def to_restart_in(self):
        newpath = self._case.path / "Restart" / f"restart_body_in.{self._iproc:05}.dat"
        shutil.copy(self._path, newpath)
        return newpath

    def __repr__(self):
        return f"RestartBody(iproc = {self._iproc}, tidx = {self._tidx})"
