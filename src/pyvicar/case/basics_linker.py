import os
from pathlib import Path
from pyvicar._tree import Field
from .input import Input
from .probe import Probe
from .canonical_body import CanonicalBody
from .unstruc_surface import UnstrucSurface
from .srj import SRJ
from .ib2 import IB2
from .nonuniform_grid import NonuniformGrid
from .job import Job
from .drag_lift import DragLiftList
from .dump import Dump
from .post import Post


def mkdir_case(self, path):
    self._path = Path(path)
    self._pathProcLog = self._path / "ProcLog"
    self._pathRestart = self._path / "Restart"
    self._pathFieldsFiles = self._path / "FieldsFiles"
    self._pathMarkerFiles = self._path / "MarkerFiles"

    self._path.mkdir(exist_ok=True)
    self._pathProcLog.mkdir(exist_ok=True)
    self._pathRestart.mkdir(exist_ok=True)
    self._pathFieldsFiles.mkdir(exist_ok=True)
    self._pathMarkerFiles.mkdir(exist_ok=True)

    return self


def link_case_children(self, restart_config_f):
    self._children.input = Input(self._path / "input.dat")
    self._children.probe = Probe(self._path / "probe_in.dat")
    self._children.canonicalBody = CanonicalBody(self._path / "canonical_body_in.dat")
    self._children.unstrucSurface = UnstrucSurface(
        self._path / "unstruc_surface_in.dat"
    )

    self._children.srj = SRJ(self._path / "SRJ_params_in.dat")

    self._children.ib2 = IB2(self._path / "ib2_in.dat")

    self._children.xgrid = NonuniformGrid(self._path / "xgrid.dat")
    self._children.ygrid = NonuniformGrid(self._path / "ygrid.dat")
    self._children.zgrid = NonuniformGrid(self._path / "zgrid.dat")

    self._children.job = Job(self, self._path / "job")

    self._children.draglift = DragLiftList(self)
    self._children.dump = Dump(self)
    self._children.restart = restart_config_f(self)
    self._children.post = Post(self)

def write_case_basics(self):
    self._children.input.write()
    self._children.probe.write()
    self._children.canonicalBody.write()
    if self._children.unstrucSurface:
        self._children.unstrucSurface.write()
    if self._children.srj:
        self._children.srj.write()
    if self._children.ib2:
        self._children.ib2.write()
    if self._children.xgrid:
        self._children.xgrid.write()
    if self._children.ygrid:
        self._children.ygrid.write()
    if self._children.zgrid:
        self._children.zgrid.write()
    if self._children.job:
        self._children.job.write()

    return self


def read_case_basics(self):
    self._children.draglift.read()
    self._children.dump.read()
    self._children.post.read()


def link_case_methods(def_nproc):
    def mpirun(self, np=None, outfile=None):
        if np is None:
            np = self.nproc
        os.system(
            f"cd {self._path}; mpirun -np {np} {self.runpath} {f'> {outfile}' if not outfile is None else f''}; cd - > /dev/null"
        )

    def sbatch(self):
        os.system(f"cd {self._path}; sbatch job; cd - > /dev/null")

    @property
    def nproc(self):
        return self.input.parallel.npx.value * self.input.parallel.npy.value

    def linker(cls):
        cls.mpirun = mpirun
        cls.sbatch = sbatch
        if def_nproc:
            cls.nproc = nproc
        return cls

    return linker
