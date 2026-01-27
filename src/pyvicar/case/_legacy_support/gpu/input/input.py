from pyvicar._tree import Group
from pyvicar.file import Writable
from pyvicar._format import write_banner
from pyvicar.case.common.input.input import add_basics, write_basics
from .time_step import TimeStepControl
from .internal_boundary import InternalBoundary
from .laplace import LaplaceSolver
from .fsi import FSI
from .misc import Misc
from pyvicar.case.common.input.mg_comments import write_mg_comment


class Input(Group, Writable):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)

        self._path = path
        self._f = open(path, "w")

        # all subgroups
        add_basics(self._children, self._f)

        # basics override, mainly change some default values
        self._children.timeStep = TimeStepControl(self._f)
        self._children.ib = InternalBoundary(self._f)

        self._children.laplace = LaplaceSolver(self._f)
        self._children.fsi = FSI(self._f)
        self._children.misc = Misc(self._f)

        self._finalize_init()

    def write(self):
        f = self._f

        write_basics(self._children, f)

        write_banner(f, "Laplace Solver (laplace)")
        self._children.laplace.write()

        write_banner(f, "FSI (fsi)")
        self._children.fsi.write()

        write_banner(f, "Version Specific Miscellaneous (misc)")
        self._children.misc.write()

        write_mg_comment(f)

        f.flush()
