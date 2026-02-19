import numpy as np
import pandas as pd
from pathlib import Path
from pyvicar._utilities import Optional
from pyvicar._tree import Group, Field, List
from pyvicar.file import Readable
from pyvicar.file import Series


class ReportList(List, Readable, Optional):
    def __init__(self, case, prefix):
        List.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._case = case
        self._prefix = prefix

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    def _elemcheck(self, new):
        if not isinstance(new, Report):
            raise TypeError(
                f"Expected a Report object inside ReportList, but encountered {repr(new)}"
            )

    def _append(self, *args, **kwargs):
        return super().append(*args, **kwargs)

    def _insert(self, *args, **kwargs):
        return super().insert(*args, **kwargs)

    def read(self):
        series = Series.from_format(self._case.path, self._prefix + r"\.(\d)\.csv")

        for file in series:
            body = Report(file.path, file.idxes[0])
            body.read()
            self._append(body)

        if series:
            self._enable()

    @property
    def prefix(self):
        return self._prefix


class Report(Group, Readable, Optional):
    def __init__(self, path, iReport=None):
        Group.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._path = Path(path)

        if iReport is not None:
            self._children.iReport = Field("iReport", iReport)

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    def read(self):
        csv = pd.read_csv(self._path)

        for key, df in csv.items():
            setattr(self._children, key, Field(key, df.to_numpy()[:, np.newaxis]))

        self._finalize_init()

        self._enable()
