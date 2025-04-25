from pyvicar._tree import Group
from pyvicar._file import Writable
from pyvicar._format import write_banner
from .parallel import ParallelConfiguration
from .domain import ComputationalDomainConfiguration
from .ic import InitialConditions
from .bc import BoundaryConditions
from .pbc import PressureBoundaryConditions
from .time_step import TimeStepControl
from .hybridization import Hybridization
from .internal_boundary import InternalBoundary
from .extended_outflow import ExtendedOutflow
from .ad import AdvectionDiffusionSolver
from .poisson import PoissonSolver
from .multigrid import MultigridMethod
from .les import LES
from .acoustics import Acoustics
from .fea import FEA
from .wall_time import WallTime
from .scalars import Scalars
from .output_format import OutputFormat
from .laplace import LaplaceSolver
from .fsi import FSI
from .shear_sensing import ShearStressSensing


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
        self._children.shearSensing = ShearStressSensing(self._f)

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

        write_banner(f, "Shear Stress Sensing (shearSensing)")
        self._children.shearSensing.write()

        write_banner(f, "Comments for MG Method")
        f.write("1. Iterations per loop\n")
        f.write(
            "   iterFinest is used for controling the number of loops at the finest level.\n"
        )
        f.write(
            "   iterCoarest is used for controling the number of loops at the coarest level.\n"
        )
        f.write(
            "   iterInter is used for other levels. If use value 0, then the number of loops will increase linearly.\n"
        )
        f.write(
            "   Tips:  1   1   1 must be used for GCM method. You may use 2 1 30 or 1 1 30 for SSM.\n"
        )
        f.write("2. total # of grid levels\n")
        f.write(
            "   0 is set by the Code, can work for most cases. Other values will be the user defined levels. You could\n"
        )
        f.write("   decide how many level can be chosen at each direction. \n")
        f.write("3. Omega\n")
        f.write("   1.0 for 2D case, better use 1.5 for 3D case. \n")
