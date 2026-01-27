from pyvicar._tree import Group
from pyvicar.file import Writable
from pyvicar._format import write_banner
from .parallel import ParallelConfiguration
from .domain import ComputationalDomainConfiguration
from .bc import BoundaryConditions
from .pbc import PressureBoundaryConditions
from .time_step import TimeStepControl
from .hybridization import Hybridization
from .internal_boundary import InternalBoundary
from .ad import AdvectionDiffusionSolver
from .poisson import PoissonSolver
from .multigrid import MultigridMethod
from .les import LES
from .fea import FEA
from .wall_time import WallTime
from .misc import Misc
from .mg_comments import write_mg_comment


def add_basics(input_children, f):
    input_children.parallel = ParallelConfiguration(f)
    input_children.domain = ComputationalDomainConfiguration(f)
    input_children.bc = BoundaryConditions(f)
    input_children.pbc = PressureBoundaryConditions(f)
    input_children.timeStep = TimeStepControl(f)
    input_children.hybridization = Hybridization(f)
    input_children.ib = InternalBoundary(f)
    input_children.ad = AdvectionDiffusionSolver(f)
    input_children.poisson = PoissonSolver(f)
    input_children.multigrid = MultigridMethod(f)
    input_children.les = LES(f)
    input_children.fea = FEA(f)
    input_children.wallTime = WallTime(f)

    return input_children


def write_basics(input_children, f):
    write_banner(f, "Parallel Configuration (parallel)")
    input_children.parallel.write()

    write_banner(f, "Computational Domain Configuration (domain)")
    input_children.domain.write()

    write_banner(f, "Boundary Conditions (bc)")
    input_children.bc.write()

    write_banner(f, "Pressure Boundary Conditions (pressurebc)")
    input_children.pbc.write()

    write_banner(f, "Time Step Control (timeStep)")
    input_children.timeStep.write()

    write_banner(f, "Hybridization (hybridization)")
    input_children.hybridization.write()

    write_banner(f, "Internal Boundary (ib)")
    input_children.ib.write()

    write_banner(f, "Advection Diffusion Solver (ad)")
    input_children.ad.write()

    write_banner(f, "Poisson Solver (poisson)")
    input_children.poisson.write()

    write_banner(f, "Multigrid Method (multigrid)")
    input_children.multigrid.write()

    write_banner(f, "LES (les)")
    input_children.les.write()

    write_banner(f, "FEA (fea)")
    input_children.fea.write()

    write_banner(f, "Wall Time (wallTime)")
    input_children.wallTime.write()


class Input(Group, Writable):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)

        self._path = path
        self._f = open(path, "w")

        # all subgroups
        add_basics(self._children, self._f)

        self._children.misc = Misc(self._f)

        self._finalize_init()

    def write(self):
        f = self._f

        write_basics(self._children, f)

        write_banner(f, "Version Specific Miscellaneous (misc)")
        self._children.misc.write()

        write_mg_comment(f)

        f.flush()
