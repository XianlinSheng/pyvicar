from pyvicar._tree import Group
from pyvicar.file import Writable
from pyvicar._format import write_banner
from .parallel import ParallelConfiguration
from pyvicar.case.common.input.input import add_basics, write_basics
from pyvicar.case.common.input.mg_comments import write_mg_comment


class Input(Group, Writable):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)

        self._path = path
        self._f = open(path, "w")

        # all subgroups
        add_basics(self._children, self._f)

        self._children.parallel = ParallelConfiguration(self._f)

        self._finalize_init()

    def write(self):
        f = self._f

        write_basics(self._children, f)

        write_mg_comment(f)

        f.flush()
