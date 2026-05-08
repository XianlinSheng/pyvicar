import numpy as np
from pathlib import Path
from pyvicar._utilities.optional import Optional
from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar.tools.miscellaneous import args


class Job(Group, Writable, Optional):
    def __init__(self, case, path, config={}):
        Group.__init__(self)
        Writable.__init__(self)
        Optional.__init__(self)

        config = args.add_default(
            config,
            {
                "ntasks": {"default": 48},
                "partition": {"default": "parallel"},
                "gres": {"default": []},
            },
            recursive=True,
        )
        self._config = config

        self._case = case
        self._path = Path(path)
        if self:
            self._init()

    def _init(self):
        self._f = open(self._path, "w")

        self._children.jobName = Field("jobName", "unnamed")
        self._children.partition = Field(
            "partition", self._config["partition"]["default"]
        )
        self._children.nodes = Field("nodes", 1)
        self._children.ntasksPerNode = Field(
            "ntasksPerNode", self._config["ntasks"]["default"]
        )
        self._children.gres = Field("gres", self._config["gres"]["default"])
        self._children.account = Field("account", "jsmith01")

        self._children.modulePurge = Field(
            "modulePurge", False, "add a module purge line in job file before mpirun"
        )
        self._children.moduleUse = Field(
            "moduleUse",
            False,
            "add a module use install/etc/modulefiles line in job file before mpirun",
        )
        self._children.moduleLoad = Field(
            "moduleLoad",
            False,
            "add a module load vicar3d/version line in job file before mpirun, version is determined by the config file etc/modulefiles/vicar3d/version",
        )

        self._children.mpinp = Field("mpinp", self._config["ntasks"]["default"])
        self._children.runpath = Field("runpath", "/path/to/executable")
        self._children.logfile = Field("logfile", "log.std")

        self._finalize_init()

    @property
    def case(self):
        return self._case

    def enable(self):
        if self:
            return
        Optional.enable(self)
        self._init()
        self.autofill()

    def write(self):
        if not self:
            raise Exception(f"The object is not active, call .enable() to enable it")

        f = self._f

        f.write(f"#!/bin/bash\n")
        f.write(f"#SBATCH --job-name='{self._children.jobName}'\n")
        f.write(f"#SBATCH --partition={self._children.partition}\n")
        f.write(f"#SBATCH --time=2-00:00:00\n")
        f.write(f"#SBATCH --nodes={self._children.nodes}\n")
        f.write(f"#SBATCH --ntasks-per-node={self._children.ntasksPerNode}\n")
        if self._children.gres.value:
            f.write(f"#SBATCH --gres={','.join(self._children.gres)}\n")
        f.write(f"#SBATCH --account={self._children.account}\n")
        f.write(f"\n")
        f.write(f"# Here starts script\n")
        if self._children.modulePurge.value:
            f.write(f"module purge\n")
        if self._children.moduleUse.value:
            # [v1.1.0 reserved] this becomes mandatory from v1.1.0 and will be checked during import
            if not self._case.installs.modulefiles.is_dir():
                raise Exception(
                    f"module use etc/modulefiles needs a valid etc/modulefiles folder but the imported ViCar3D version does not support one"
                )
            f.write(f"module use {self._case.installs.modulefiles}\n")
        if self._children.moduleLoad.value:
            # [v1.1.0 reserved] this becomes mandatory from v1.1.0 and will be checked during import
            if self._case.installs.version == "none":
                raise Exception(
                    f"module load vicar3d/version needs a valid etc/modulefiles/vicar3d/version config file but the imported ViCar3D version does not support one"
                )
            f.write(f"module load vicar3d/{self._case.installs.version}\n")
        f.write(f"\n")
        f.write(
            f"mpirun -np {self._children.mpinp} {self._children.runpath} > {self._children.logfile}\n"
        )
        f.write(f"\n")

        f.flush()

    # fill job np, mpi np, run path from current case config
    def autofill(self):
        nproc = self._case.nproc
        self._children.jobName.value = self._case.name
        self._children.nodes.value = int(
            np.ceil(nproc / self._children.ntasksPerNode.value)
        )
        self._children.mpinp.value = nproc
        self._children.runpath.value = str(self._case.runpath)
