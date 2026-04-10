import numpy as np
import pandas as pd
from pathlib import Path
from pyvicar._utilities import Optional
from pyvicar._tree import Group, Field, List
from pyvicar.file import Readable
from pyvicar.file import Series


class RHMStatList(List, Readable, Optional):
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
        if not isinstance(new, RHMStat):
            raise TypeError(
                f"Expected a RHMStat object inside RHMStatList, but encountered {repr(new)}"
            )

    def _append(self, *args, **kwargs):
        return super().append(*args, **kwargs)

    def _insert(self, *args, **kwargs):
        return super().insert(*args, **kwargs)

    def read(self):
        series = Series.from_format(self._case.path, r"rhm_stat_body_(\d{3})\.csv")
        iBody = 1
        for file in series:
            # non-rhm bodies between two, insert empty placeholders, so bodies can still be accessed by iBody
            # but larger index do not exist
            while iBody != file.idxes[0]:
                self._append(RHMStat(None, iBody))
                iBody += 1

            body = RHMStat(file.path, file.idxes[0])
            body.read()
            self._append(body)
            iBody += 1

        if series:
            self._enable()


class RHMStat(Group, Readable, Optional):
    def __init__(self, path, iBody):
        Group.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._path = Path(path) if not path is None else None

        self._children.iBody = Field("iBody", iBody)

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    def read(self):
        if self._path is None:
            raise Exception(
                f"RHMStat handle is invalid and cannot be read. This often indicates that the body is not in RHM type"
            )

        csv = pd.read_csv(self._path)

        self._children.time = Field("time", csv["time"].to_numpy()[:, np.newaxis])

        self._children.xcentBody = Field(
            "xcentBody", csv["xcent_body"].to_numpy()[:, np.newaxis]
        )
        self._children.ycentBody = Field(
            "ycentBody", csv["ycent_body"].to_numpy()[:, np.newaxis]
        )
        self._children.zcentBody = Field(
            "zcentBody", csv["zcent_body"].to_numpy()[:, np.newaxis]
        )

        self._children.xcentBase = Field(
            "xcentBase", csv["xcent_base"].to_numpy()[:, np.newaxis]
        )
        self._children.ycentBase = Field(
            "ycentBase", csv["ycent_base"].to_numpy()[:, np.newaxis]
        )
        self._children.zcentBase = Field(
            "zcentBase", csv["zcent_base"].to_numpy()[:, np.newaxis]
        )

        self._children.angxBody = Field(
            "angxBody", csv["angx_body"].to_numpy()[:, np.newaxis]
        )
        self._children.angyBody = Field(
            "angyBody", csv["angy_body"].to_numpy()[:, np.newaxis]
        )
        self._children.angzBody = Field(
            "angzBody", csv["angz_body"].to_numpy()[:, np.newaxis]
        )

        self._children.angxBase = Field(
            "angxBase", csv["angx_base"].to_numpy()[:, np.newaxis]
        )
        self._children.angyBase = Field(
            "angyBase", csv["angy_base"].to_numpy()[:, np.newaxis]
        )
        self._children.angzBase = Field(
            "angzBase", csv["angz_base"].to_numpy()[:, np.newaxis]
        )

        self._finalize_init()
        self._enable()
