from pathlib import Path
from pyvicar._tree import Group
from pyvicar._file import Writable
from .input import Input
from .probe import Probe
from .canonical_body import CanonicalBody
from .unstruc_surface import UnstrucSurface
from .nonuniform_grid import NonuniformGrid
from .drag_lift import DragLiftList
from .dump import Dump
from .post import Post


class Case(Group, Writable):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)

        self._path = Path(path)
        self._pathProcLog = self._path / "ProcLog"
        self._pathRestart = self._path / "Restart"
        self._pathQFiles = self._path / "qFiles"
        self._pathMarkerFiles = self._path / "MarkerFiles"

        self._path.mkdir(exist_ok=True)
        self._pathProcLog.mkdir(exist_ok=True)
        self._pathRestart.mkdir(exist_ok=True)
        self._pathQFiles.mkdir(exist_ok=True)
        self._pathMarkerFiles.mkdir(exist_ok=True)

        self._children.input = Input(self._path / "input.dat")
        self._children.probe = Probe(self._path / "probe_in.dat")
        self._children.canonicalBody = CanonicalBody(
            self._path / "canonical_body_in.dat"
        )
        self._children.unstrucSurface = UnstrucSurface(
            self._path / "unstruc_surface_in.dat"
        )
        self._children.xgrid = NonuniformGrid(self._path / "xgrid.dat")
        self._children.ygrid = NonuniformGrid(self._path / "ygrid.dat")
        self._children.zgrid = NonuniformGrid(self._path / "zgrid.dat")

        self._children.draglift = DragLiftList(self)
        self._children.dump = Dump(self)
        self._children.post = Post(self)

        self._finalize_init()

    @property
    def path(self):
        return self._path

    def write(self):
        self._children.input.write()
        self._children.probe.write()
        self._children.canonicalBody.write()
        if self._children.unstrucSurface:
            self._children.unstrucSurface.write()
        if self._children.xgrid:
            self._children.xgrid.write()
        if self._children.ygrid:
            self._children.ygrid.write()
        if self._children.zgrid:
            self._children.zgrid.write()

    def read(self):
        self._children.draglift.read()
        self._children.dump.read()
        self._children.post.read()
