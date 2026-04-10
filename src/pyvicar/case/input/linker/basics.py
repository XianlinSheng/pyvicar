from pyvicar._format import write_banner
from pyvicar.case.input.parallel import ParallelConfiguration
from pyvicar.case.input.domain import ComputationalDomainConfiguration
from pyvicar.case.input.bc import BoundaryConditions
from pyvicar.case.input.pbc import PressureBoundaryConditions
from pyvicar.case.input.time_step import TimeStepControl
from pyvicar.case.input.hybridization import Hybridization
from pyvicar.case.input.internal_boundary import InternalBoundary
from pyvicar.case.input.ad import AdvectionDiffusionSolver
from pyvicar.case.input.poisson import PoissonSolver
from pyvicar.case.input.multigrid import MultigridMethod
from pyvicar.case.input.les import LES
from pyvicar.case.input.fea import FEA
from pyvicar.case.input.wall_time import WallTime
from pyvicar.case.input.misc import Misc
from pyvicar.case.input.mg_comments import write_mg_comment
from pyvicar.tools.miscellaneous import args


class BasicsLinker:
    @staticmethod
    def def_path(self, path):
        self._path = path
        self._f = open(path, "w")

        return self

    _default_children = {
        "parallel": True,
        "domain": True,
        "bc": True,
        "pbc": True,
        "timeStep": True,
        "hybridization": True,
        "ib": True,
        "ad": True,
        "poisson": True,
        "multigrid": True,
        "les": True,
        "fea": True,
        "wallTime": True,
        "misc": True,
    }

    @staticmethod
    def def_children(self, def_list={}, config={}):
        def_list = args.add_default(def_list, BasicsLinker._default_children)

        config = args.add_default(
            config, {"misc_cls": Misc, "bc": {}, "ib": {}, "poisson": {}}
        )

        f = self._f

        if def_list["parallel"]:
            self._children.parallel = ParallelConfiguration(f)

        if def_list["domain"]:
            self._children.domain = ComputationalDomainConfiguration(f)

        if def_list["bc"]:
            self._children.bc = BoundaryConditions(f, config=config["bc"])

        if def_list["pbc"]:
            self._children.pbc = PressureBoundaryConditions(f)

        if def_list["timeStep"]:
            self._children.timeStep = TimeStepControl(f)

        if def_list["hybridization"]:
            self._children.hybridization = Hybridization(f)

        if def_list["ib"]:
            self._children.ib = InternalBoundary(f, config=config["ib"])

        if def_list["ad"]:
            self._children.ad = AdvectionDiffusionSolver(f)

        if def_list["poisson"]:
            self._children.poisson = PoissonSolver(f, config=config["poisson"])

        if def_list["multigrid"]:
            self._children.multigrid = MultigridMethod(f)

        if def_list["les"]:
            self._children.les = LES(f)

        if def_list["fea"]:
            self._children.fea = FEA(f)

        if def_list["wallTime"]:
            self._children.wallTime = WallTime(f)

        if def_list["misc"]:
            self._children.misc = config["misc_cls"](f)

        return self

    def write_children(self, def_list={}):
        def_list = args.add_default(def_list, BasicsLinker._default_children)

        f = self._f

        if def_list["parallel"]:
            write_banner(f, "Parallel Configuration (parallel)")
            self._children.parallel.write()

        if def_list["domain"]:
            write_banner(f, "Computational Domain Configuration (domain)")
            self._children.domain.write()

        if def_list["bc"]:
            write_banner(f, "Boundary Conditions (bc)")
            self._children.bc.write()

        if def_list["pbc"]:
            write_banner(f, "Pressure Boundary Conditions (pbc)")
            self._children.pbc.write()

        if def_list["timeStep"]:
            write_banner(f, "Time Step Control (timeStep)")
            self._children.timeStep.write()

        if def_list["hybridization"]:
            write_banner(f, "Hybridization (hybridization)")
            self._children.hybridization.write()

        if def_list["ib"]:
            write_banner(f, "Internal Boundary (ib)")
            self._children.ib.write()

        if def_list["ad"]:
            write_banner(f, "Advection Diffusion Solver (ad)")
            self._children.ad.write()

        if def_list["poisson"]:
            write_banner(f, "Poisson Solver (poisson)")
            self._children.poisson.write()

        if def_list["multigrid"]:
            write_banner(f, "Multigrid Method (multigrid)")
            self._children.multigrid.write()

        if def_list["les"]:
            write_banner(f, "LES (les)")
            self._children.les.write()

        if def_list["fea"]:
            write_banner(f, "FEA (fea)")
            self._children.fea.write()

        if def_list["wallTime"]:
            write_banner(f, "Wall Time (wallTime)")
            self._children.wallTime.write()

        if def_list["misc"]:
            write_banner(f, "Version Specific Miscellaneous (misc)")
            self._children.misc.write()

        write_mg_comment(f)

        return self
