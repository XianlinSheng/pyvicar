from pyvicar._tree import Group
from pyvicar.file import Writable
from pyvicar._format import KV1Formatter
from .general import General
from pyvicar.case.common.canonical_body.body.body import add_basics, write_basics


class Body(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)
        self._f = f

        add_basics(self._children, self._f)

        self._children.general = General(self._f)

        self._finalize_init()

    def write(self):
        write_basics(self._children)
