from pyvicar._utilities import Optional
from pyvicar._tree import Group
from pyvicar._file import Readable
from .animations import AnimationDict
from .reports import ReportDict


class Post(Group, Readable, Optional):
    def __init__(self, case):
        Group.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._case = case
        self._path = self._case.path / "Post"

    def _init(self):
        self._path.mkdir(exist_ok=True)

        self._children.animations = AnimationDict(self)
        self._children.reports = ReportDict(self)

        self._finalize_init()

    def enable(self):
        super().enable()
        self._init()

    def _disable(self):
        return super().disable()

    def read(self):
        if not self._path.exists():
            return

        self.enable()
        self._children.animations.read()
        self._children.reports.read()

    @property
    def path(self):
        return self._path
