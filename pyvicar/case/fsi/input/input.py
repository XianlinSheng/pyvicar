from pyvicar._tree import Group
from pyvicar.file import Writable
from pyvicar._format import write_banner
from pyvicar.case.common.input.parallel import ParallelConfiguration
from pyvicar.case.common.input.domain import ComputationalDomainConfiguration
from pyvicar.case.common.input.ic import InitialConditions
from .bc import BoundaryConditions
from pyvicar.case.common.input.pbc import PressureBoundaryConditions
from pyvicar.case.common.input.time_step import TimeStepControl
from pyvicar.case.common.input.hybridization import Hybridization
from pyvicar.case.common.input.internal_boundary import InternalBoundary
from pyvicar.case.common.input.extended_outflow import ExtendedOutflow
from pyvicar.case.common.input.ad import AdvectionDiffusionSolver
from .poisson import PoissonSolver
from pyvicar.case.common.input.multigrid import MultigridMethod
from pyvicar.case.common.input.les import LES
from pyvicar.case.common.input.acoustics import Acoustics
from pyvicar.case.common.input.fea import FEA
from pyvicar.case.common.input.wall_time import WallTime
from .scalars import Scalars
from pyvicar.case.common.input.output_format import OutputFormat
from .laplace import LaplaceSolver
from .fsi import FSI
from .poisson_history import PoissonHistory
from pyvicar.case.common.input.mg_comments import write_mg_comment


class Input(Group, Writable):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)

        self._path = path
        self._f = open(path, "w")

        # all subgroups
        self._children.parallel = ParallelConfiguration(self._f)
        self._children.domain = ComputationalDomainConfiguration(self._f)
        self._children.ic = InitialConditions(self._f)
        self._children.bc = BoundaryConditions(self._f)
        self._children.pbc = PressureBoundaryConditions(self._f)
        self._children.timeStep = TimeStepControl(self._f)
        self._children.hybridization = Hybridization(self._f)
        self._children.internalBoundary = InternalBoundary(self._f)
        self._children.extendedOutflow = ExtendedOutflow(self._f)
        self._children.ad = AdvectionDiffusionSolver(self._f)
        self._children.poisson = PoissonSolver(self._f)
        self._children.multigrid = MultigridMethod(self._f)
        self._children.les = LES(self._f)
        self._children.acoustics = Acoustics(self._f)
        self._children.fea = FEA(self._f)
        self._children.wallTime = WallTime(self._f)
        self._children.scalars = Scalars(self._f)
        self._children.outputFormat = OutputFormat(self._f)
        self._children.laplace = LaplaceSolver(self._f)
        self._children.fsi = FSI(self._f)
        self._children.poissonHistory = PoissonHistory(self._f)

        self._finalize_init()

    def write(self):
        f = self._f

        write_banner(f, "Parallel Configuration (parallel)")
        self._children.parallel.write()

        write_banner(f, "Computational Domain Configuration (domain)")
        self._children.domain.write()

        write_banner(f, "Initial Conditions (ic)")
        self._children.ic.write()

        write_banner(f, "Boundary Conditions (bc)")
        self._children.bc.write()

        write_banner(f, "Pressure Boundary Conditions (pressurebc)")
        self._children.pbc.write()

        write_banner(f, "Time Step Control (timeStep)")
        self._children.timeStep.write()

        write_banner(f, "Hybridization (hybridization)")
        self._children.hybridization.write()

        write_banner(f, "Internal Boundary (internalBoundary)")
        self._children.internalBoundary.write()

        write_banner(f, "Extended Outflow (extendedOutflow)")
        self._children.extendedOutflow.write()

        write_banner(f, "Advection Diffusion Solver (ad)")
        self._children.ad.write()

        write_banner(f, "Poisson Solver (poisson)")
        self._children.poisson.write()

        write_banner(f, "Multigrid Method (multigrid)")
        self._children.multigrid.write()

        write_banner(f, "LES (les)")
        self._children.les.write()

        write_banner(f, "Acoustics (acoustics)")
        self._children.acoustics.write()

        write_banner(f, "FEA (fea)")
        self._children.fea.write()

        write_banner(f, "Wall Time (wallTime)")
        self._children.wallTime.write()

        write_banner(f, "Scalars and Other Flags (scalars)")
        self._children.scalars.write()

        write_banner(f, "Output Format (outputFormat)")
        self._children.outputFormat.write()

        write_banner(f, "Laplace Solver (laplace)")
        self._children.laplace.write()

        write_banner(f, "FSI (fsi)")
        self._children.fsi.write()

        write_banner(f, "Poisson History (poissonHistory)")
        self._children.poissonHistory.write()

        write_mg_comment(f)

        f.flush()
