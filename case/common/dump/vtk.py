import pyvista as pv
from mpi4py import MPI
from dataclasses import dataclass
from collections.abc import Iterable
from pyvicar._tree import List
from pyvicar._file import Readable, Series
from pyvicar._utilities import Optional


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


class VTKList(List, Readable, Optional):
    def __init__(self, case):
        List.__init__(self)
        Readable.__init__(self)
        self._case = case

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    def _elemcheck(self, new):
        if not isinstance(new, VTK):
            raise TypeError(
                f"Expected a VTK object inside VTKList, but encountered {repr(new)}"
            )

    def _append(self, *args, **kwargs):
        return super().append(*args, **kwargs)

    def _insert(self, *args, **kwargs):
        return super().insert(*args, **kwargs)

    def read(self):
        series = Series.from_format(self._case.path / "qFiles", r"fields\.(\d+)\.vtm")
        for file in series:
            vtk = VTK(file.path, file.idxes[0])
            self._append(vtk)

        if series:
            self._enable()

    @property
    def latest(self):
        if not self:
            raise Exception(f"VTKList is not active now")

        return self[self._startidx - 1]

    def mpi_dispatch_frames(self):
        # calculate the frames and dispatch views to each processor
        if rank == 0:
            total = len(self)
            eachbase = total // size
            extra = total - eachbase * size
            nframes = [eachbase] * size
            # nframes[0] += extra
            nframes = [eachbase + 1 if i < extra else eachbase for i in range(size)]

            views = []
            ptr = self._startidx
            for nframe in nframes:
                view = MPIJob(ptr, ptr + nframe)
                views.append(view)
                ptr += nframe

            # dispatch views
            for i in range(size):
                if i == 0:
                    view = views[0]
                    view.set_parent(self)
                else:
                    comm.send(views[i], dest=i, tag=i)
        else:
            view = comm.recv(source=0, tag=rank)
            view.set_parent(self)

        return view


class MPIJob(Iterable):
    # start stop are based on VTKList offsetted index
    def __init__(self, start, stop):
        self._parent = None
        self._start = start
        self._stop = stop
        self._nframe = stop - start

    @property
    def parent(self):
        return self._parent

    @property
    def start(self):
        return self._start

    @property
    def stop(self):
        return self._stop

    @property
    def nframe(self):
        return self._nframe

    @property
    def startidx(self):
        return self._parent.startidx

    def set_parent(self, parent):
        self._parent = parent

    def __iter__(self):
        return iter(self._parent[self._start : self._stop])

    def __repr__(self):
        return f"MPIJob(VTKList[{self._start} : {self._stop}] @ Proc {rank})"


class VTK:
    def __init__(self, path, tstep):
        self._path = path
        self._tstep = tstep

    @property
    def path(self):
        return self._path

    @property
    def tstep(self):
        return self._tstep

    def to_pyvista_multiblocks(self):
        return pv.read(self._path)

    def to_pyvista(self):
        return pv.read(self._path).combine()

    def __repr__(self):
        return f"VTK(tstep = {self._tstep})"
