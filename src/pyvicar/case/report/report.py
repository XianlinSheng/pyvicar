from pyvicar._tree import Group
from pyvicar.file import Readable
from pyvicar._utilities import Optional
from .report_list import ReportList


class Report(Group, Readable, Optional):
    def __init__(self, case, configs):
        Group.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._case = case
        self._path = case.path

        for config in configs:
            prefix = config["prefix"]
            if config["list"]:
                setattr(
                    self._children,
                    prefix,
                    ReportList(case, prefix),
                )
            else:
                setattr(
                    self._children,
                    prefix,
                    Report(case, self._path / f"{prefix}.csv"),
                )

        self._finalize_init()

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    def read(self):
        for obj in self._children.values():
            obj.read()
        if any(self._children.values()):
            self._enable()

    @property
    def path(self):
        return self._path
