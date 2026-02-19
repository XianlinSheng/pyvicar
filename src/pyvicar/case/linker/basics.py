import os
import json
from pathlib import Path
from pyvicar.case.input import Input
from pyvicar.case.probe import Probe
from pyvicar.case.canonical_body import CanonicalBody
from pyvicar.case.unstruc_surface import UnstrucSurface
from pyvicar.case.srj import SRJ
from pyvicar.case.nonuniform_grid import NonuniformGrid
from pyvicar.case.job import Job
from pyvicar.case.drag_lift import DragLiftList
from pyvicar.case.dump import Dump
from pyvicar.case.post import Post
from pyvicar.case.restart import Restart
from pyvicar.case.report import Report
from pyvicar.tools.miscellaneous import args


class BasicsLinker:
    @staticmethod
    def def_path(
        self,
        path,
        def_list={},
    ):
        def_list = args.add_default(
            def_list,
            {
                "proclog": True,
                "restart": True,
                "fields": True,
                "marker": True,
            },
        )

        self._path = Path(path)
        self._path.mkdir(exist_ok=True)

        if def_list["proclog"]:
            self._pathProcLog = self._path / "ProcLog"
            self._pathProcLog.mkdir(exist_ok=True)

        if def_list["restart"]:
            self._pathRestart = self._path / "Restart"
            self._pathRestart.mkdir(exist_ok=True)

        if def_list["fields"]:
            self._pathFieldsFiles = self._path / "FieldsFiles"
            self._pathFieldsFiles.mkdir(exist_ok=True)

        if def_list["marker"]:
            self._pathMarkerFiles = self._path / "MarkerFiles"
            self._pathMarkerFiles.mkdir(exist_ok=True)

        return self

    _default_w_children = {
        "input": True,
        "probe": True,
        "cbody": True,
        "usurf": True,
        "srj": True,
        "grids": True,
        "job": True,
    }

    _default_r_children = {
        "draglift": True,
        "dump": True,
        "restart": True,
        "report": True,
        "post": True,
    }

    _default_children = _default_r_children | _default_w_children

    @staticmethod
    def def_children(
        self,
        def_list={},
        config={},
    ):
        def_list = args.add_default(def_list, BasicsLinker._default_children)

        config = args.add_default(
            config,
            {
                "cbody_cls": CanonicalBody,
                "input_cls": Input,
                "cbody": {},
                "input": {},
                "restart": [],
                "report": [],
            },
        )

        self._config = config

        if def_list["input"]:
            self._children.input = config["input_cls"](
                self._path / "input.dat", config=config["input"]
            )

        if def_list["probe"]:
            self._children.probe = Probe(self._path / "probe_in.dat")

        if def_list["cbody"]:
            self._children.canonicalBody = config["cbody_cls"](
                self._path / "canonical_body_in.dat",
                config=config["cbody"],
            )

        if def_list["usurf"]:
            self._children.unstrucSurface = UnstrucSurface(
                self._path / "unstruc_surface_in.dat"
            )

        if def_list["srj"]:
            self._children.srj = SRJ(self._path / "SRJ_params_in.dat")

        if def_list["grids"]:
            self._children.xgrid = NonuniformGrid(self._path / "xgrid.dat")
            self._children.ygrid = NonuniformGrid(self._path / "ygrid.dat")
            self._children.zgrid = NonuniformGrid(self._path / "zgrid.dat")

        if def_list["job"]:
            self._children.job = Job(self, self._path / "job")

        if def_list["draglift"]:
            self._children.draglift = DragLiftList(self)

        if def_list["dump"]:
            self._children.dump = Dump(self)

        if def_list["restart"]:
            self._children.restart = Restart(self, configs=config["restart"])

        if def_list["report"]:
            self._children.report = Report(self, configs=config["report"])

        if def_list["post"]:
            self._children.post = Post(self)

        return self

    @staticmethod
    def write_children(
        self,
        def_list={},
    ):
        def_list = args.add_default(def_list, BasicsLinker._default_w_children)

        if def_list["input"]:
            self._children.input.write()

        if def_list["probe"]:
            self._children.probe.write()

        if def_list["cbody"]:
            self._children.canonicalBody.write()

        if def_list["usurf"] and self._children.unstrucSurface:
            self._children.unstrucSurface.write()

        if def_list["srj"] and self._children.srj:
            self._children.srj.write()

        if def_list["grids"]:
            if self._children.xgrid:
                self._children.xgrid.write()
            if self._children.ygrid:
                self._children.ygrid.write()
            if self._children.zgrid:
                self._children.zgrid.write()

        if def_list["job"] and self._children.job:
            self._children.job.write()

        return self

    @staticmethod
    def read_children(
        self,
        def_list={},
    ):
        def_list = args.add_default(def_list, BasicsLinker._default_r_children)

        if def_list["draglift"]:
            self._children.draglift.read()

        if def_list["dump"]:
            self._children.dump.read()

        if def_list["restart"]:
            self._children.restart.read()

        if def_list["report"]:
            self._children.report.read()

        if def_list["post"]:
            self._children.post.read()

        return self

    @staticmethod
    def def_methods(def_list={}):
        def_list = args.add_default(
            def_list,
            {
                "path": True,
                "mpirun": True,
                "sbatch": True,
                "nproc": True,
                "config": True,
            },
        )

        @property
        def path(self):
            return self._path

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

        @property
        def config(self):
            return self._config

        @property
        def config_json(self):
            return json.dumps(self._config, indent=2, default=lambda obj: str(obj))

        def linker(cls):
            if def_list["path"]:
                cls.path = path
            if def_list["mpirun"]:
                cls.mpirun = mpirun
            if def_list["sbatch"]:
                cls.sbatch = sbatch
            if def_list["nproc"]:
                cls.nproc = nproc
            if def_list["config"]:
                cls.config = config
                cls.config_json = config_json

            return cls

        return linker
