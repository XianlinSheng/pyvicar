import numpy as np
import pandas as pd
from pathlib import Path
from pyvicar._utilities import Optional
from pyvicar._tree import Group, Field, List
from pyvicar.file import Readable
from pyvicar.file import Series


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


class DragLift(Group, Readable):
    def __init__(self, path, bodyi):
        Group.__init__(self)
        Readable.__init__(self)
        self._path = Path(path)

        self._children.bodyi = Field("bodyi", bodyi)

    def read(self):
        csv = pd.read_csv(self._path)

        self._children.time = Field("time", csv["time"].to_numpy()[:, np.newaxis])

        self._children.cxp = Field("cxp", csv["cxp"].to_numpy()[:, np.newaxis])
        self._children.cxs = Field("cxs", csv["cxs"].to_numpy()[:, np.newaxis])
        self._children.cx = Field("cx", csv["cx"].to_numpy()[:, np.newaxis])

        self._children.cyp = Field("cyp", csv["cyp"].to_numpy()[:, np.newaxis])
        self._children.cys = Field("cys", csv["cys"].to_numpy()[:, np.newaxis])
        self._children.cy = Field("cy", csv["cy"].to_numpy()[:, np.newaxis])

        self._children.czp = Field("czp", csv["czp"].to_numpy()[:, np.newaxis])
        self._children.czs = Field("czs", csv["czs"].to_numpy()[:, np.newaxis])
        self._children.cz = Field("cz", csv["cz"].to_numpy()[:, np.newaxis])

        self._children.cmxp = Field("cmxp", csv["cmxp"].to_numpy()[:, np.newaxis])
        self._children.cmxs = Field("cmxs", csv["cmxs"].to_numpy()[:, np.newaxis])
        self._children.cmx = Field("cmx", csv["cmx"].to_numpy()[:, np.newaxis])

        self._children.cmyp = Field("cmyp", csv["cmyp"].to_numpy()[:, np.newaxis])
        self._children.cmys = Field("cmys", csv["cmys"].to_numpy()[:, np.newaxis])
        self._children.cmy = Field("cmy", csv["cmy"].to_numpy()[:, np.newaxis])

        self._children.cmzp = Field("cmzp", csv["cmzp"].to_numpy()[:, np.newaxis])
        self._children.cmzs = Field("cmzs", csv["cmzs"].to_numpy()[:, np.newaxis])
        self._children.cmz = Field("cmz", csv["cmz"].to_numpy()[:, np.newaxis])

        self._children.cpwx = Field("cpwx", csv["cpwx"].to_numpy()[:, np.newaxis])
        self._children.cpwy = Field("cpwy", csv["cpwy"].to_numpy()[:, np.newaxis])
        self._children.cpwz = Field("cpwz", csv["cpwz"].to_numpy()[:, np.newaxis])
        self._children.cpw = Field("cpw", csv["cpw"].to_numpy()[:, np.newaxis])

        self._children.surfaceArea = Field("surfaceArea", csv["surfaceArea"])

        self._finalize_init()
