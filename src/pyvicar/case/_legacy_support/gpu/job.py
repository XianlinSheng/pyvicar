import numpy as np
from pathlib import Path
from pyvicar._utilities.optional import Optional
from pyvicar._tree import Group, Field
from pyvicar.file import Writable


class Job(Group, Writable, Optional):
    def __init__(self, case, path):
        Group.__init__(self)
        Writable.__init__(self)
        Optional.__init__(self)
        self._case = case
        self._path = Path(path)
        if self:
            self._init()

    def _init(self):
        self._f = open(self._path, "w")

        self._children.jobName = Field("jobName", "unnamed")
        self._children.partition = Field("partition", "a100")
        self._children.nodes = Field("nodes", 1)
        self._children.ntasksPerNode = Field("ntasksPerNode", 4)
        self._children.account = Field("account", "")
        self._children.mpinp = Field("mpinp", 4)
        self._children.runpath = Field(
            "runpath", "~/Vicar3D/versions/version/src/Vicar3D"
        )
        self._children.logfile = Field("logfile", "log.std")

        self._finalize_init()

    @property
    def case(self):
        return self._case

    def enable(self):
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
        f.write(f"#SBATCH --gpus-per-node={self._children.ntasksPerNode}\n")
        f.write(f"#SBATCH --account={self._children.account}\n")
        f.write(f"\n")
        f.write(f"# Here starts script\n")
        f.write(
            f"mpirun -np {self._children.mpinp} {self._children.runpath} > {self._children.logfile}\n"
        )
        f.write(f"\n")

        f.flush()

    # fill job np, mpi np, run path from current case config
    def autofill(self):
        nproc = self._case.nproc
        self._children.nodes = int(np.ceil(nproc / self._children.ntasksPerNode.value))
        self._children.mpinp = nproc
        self._children.runpath = self._case._children.runpath.value
