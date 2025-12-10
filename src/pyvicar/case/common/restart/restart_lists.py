import shutil
from pyvicar._tree import List, Group
from pyvicar.file import Readable, Series
from pyvicar._utilities import Optional


class RestartLists(Group, Readable, Optional):
    def __init__(self, case, prefix, partitioned):
        Group.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._case = case
        self._prefix = prefix
        self._partitioned = partitioned

        self._children.t1 = RestartList(self._case, prefix, partitioned, 1)
        self._children.t2 = RestartList(self._case, prefix, partitioned, 2)

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
            raise Exception(f"No active restart {self._prefix} out files")

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

    @property
    def prefix(self):
        return self._prefix

    @property
    def partitioned(self):
        return self._partitioned


class RestartList(List, Readable, Optional):
    def __init__(self, case, prefix, partitioned, tidx):
        List.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._case = case
        self._prefix = prefix
        self._partitioned = partitioned
        self._tidx = tidx

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    def _elemcheck(self, new):
        if not isinstance(new, RestartFile):
            raise TypeError(
                f"Expected a RestartFile object inside RestartList, but encountered {repr(new)}"
            )
        if new.prefix != self._prefix:
            raise TypeError(
                f"Expected a {self._prefix} RestartFile inside {self._prefix} RestartList, but encountered {new.prefix}"
            )

    def _append(self, *args, **kwargs):
        return super().append(*args, **kwargs)

    def _insert(self, *args, **kwargs):
        return super().insert(*args, **kwargs)

    def read(self):
        series = Series.from_format(
            self._case.path / "Restart",
            (
                f"restart_{self._prefix}_out"
                + get_iproc_fmt(self._partitioned)
                + f".{self._tidx}"
                + f".dat"
            ),
        )
        for file in series:
            idx = file.idxes[0] if self._partitioned else None
            restart = RestartFile(self._case, self._prefix, file.path, idx, self._tidx)
            self._append(restart)

        if series:
            self._enable()

    @property
    def tidx(self):
        return self._tidx

    @property
    def prefix(self):
        return self._prefix

    @property
    def partitioned(self):
        return self._partitioned

    def to_restart_in(self):
        if not self:
            raise Exception(f"No active restart {self._prefix} in files")

        for flow in self._childrenlist:
            flow.to_restart_in()


class RestartFile:
    def __init__(self, case, prefix, path, iproc, tidx):
        self._case = case
        self._prefix = prefix
        self._path = path
        self._iproc = iproc
        self._tidx = tidx

    @property
    def prefix(self):
        return self._prefix

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
        newpath = (
            self._case.path
            / "Restart"
            / f"restart_{self._prefix}_in{get_iproc_str(self._iproc)}.dat"
        )
        shutil.copy(self._path, newpath)
        return newpath

    def __repr__(self):
        return f"RestartFile(prefix = {self._prefix}, iproc = {self._iproc}, tidx = {self._tidx})"


def get_iproc_fmt(partitioned):
    return r"\.(\d{5})" if partitioned else ""


def get_iproc_str(iproc):
    return f".{iproc:05}" if iproc is not None else ""
