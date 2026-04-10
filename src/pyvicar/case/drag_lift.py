import numpy as np
import pandas as pd
from pathlib import Path
from pyvicar._utilities import Optional
from pyvicar._tree import Group, Field, List
from pyvicar.file import Readable
from pyvicar.file import Series
from pyvicar.tools.post.time import proc_draglift


class DragLiftList(List, Readable, Optional):
    def __init__(self, case):
        List.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._case = case

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    def _elemcheck(self, new):
        if not isinstance(new, DragLift):
            raise TypeError(
                f"Expected a DragLift object inside DragLiftList, but encountered {repr(new)}"
            )

    def _append(self, *args, **kwargs):
        return super().append(*args, **kwargs)

    def _insert(self, *args, **kwargs):
        return super().insert(*args, **kwargs)

    def read(self):
        series = Series.from_format(self._case.path, r"drag_lift_body_(\d{3})\.csv")
        for file in series:
            body = DragLift(file.path, file.idxes[0])
            body.read()
            self._append(body)

        if series:
            self._enable()

    def proc(self, *args, **kwargs):
        return proc_draglift(self, *args, **kwargs)


class DragLift(Group, Readable):
    def __init__(self, path, iBody):
        Group.__init__(self)
        Readable.__init__(self)
        self._path = Path(path)

        self._children.iBody = Field("iBody", iBody)

    def read(self):
        csv = pd.read_csv(self._path)

        for key, df in csv.items():
            setattr(self._children, key, Field(key, df.to_numpy()[:, np.newaxis]))

        self._finalize_init()
