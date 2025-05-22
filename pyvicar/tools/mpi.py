from mpi4py import MPI
from collections.abc import Iterable, Sequence
from itertools import product
from enum import Enum
import time
from datetime import timedelta
from pyvicar.tools.miscellaneous import split_into_n


_comm = MPI.COMM_WORLD
_rank = _comm.Get_rank()
_size = _comm.Get_size()

_is_host = _rank == 0

_start_time = time.time()


def barrier():
    return _comm.Barrier()


class ParallelMode(Enum):
    Sync = 0
    Async = 1


_parallelmode = ParallelMode.Sync


def comm():
    return _comm


def rank():
    return _rank


def size():
    return _size


def parallel_mode():
    return _parallelmode


def set_sync():
    global _parallelmode
    _parallelmode = ParallelMode.Sync
    _comm.Barrier()


def set_async():
    global _parallelmode
    _comm.Barrier()
    _parallelmode = ParallelMode.Async


def is_sync():
    return _parallelmode == ParallelMode.Sync


def is_async():
    return _parallelmode == ParallelMode.Async


def is_host():
    return _is_host


def is_synchost_or_async():
    return (
        _parallelmode == ParallelMode.Sync
        and _rank == 0
        or _parallelmode == ParallelMode.Async
    )


def barrier_or_async():
    if _parallelmode == ParallelMode.Sync:
        _comm.Barrier()


def dispatch_sequence(listobj: Sequence, startidx=0):
    # calculate the elements and dispatch views to each processor
    if _rank == 0:
        nelems = split_into_n(len(listobj), _size)
        # reverse is used to relieve proc 0
        nelems.reverse()

        views = []
        ptr = startidx
        for nelem in nelems:
            view = MPIView(ptr, ptr + nelem, startidx)
            views.append(view)
            ptr += nelem

        # dispatch views
        for i in range(_size):
            if i == 0:
                view = views[0]
                view.set_parent(listobj)
            else:
                _comm.send(views[i], dest=i, tag=i)
    else:
        view = _comm.recv(source=0, tag=_rank)
        view.set_parent(listobj)

    return view


# dispatch an Iterable, first create indexed list as its parent
def dispatch(listobj: Iterable):
    # refer to a list, so startidx must = 0
    return dispatch_sequence(list(listobj), 0)


def prod_and_dispatch(*args):
    return dispatch(product(*args))


class MPIView(Iterable):
    # start stop are based on VTKList offsetted index
    def __init__(self, start, stop, startidx=1):
        self._parent = None
        self._start = start
        self._stop = stop
        self._nframe = stop - start
        self._startidx = startidx

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
        return self._startidx

    def set_parent(self, parent):
        self._parent = parent

    def __iter__(self):
        return iter(self._parent[self._start : self._stop])

    def __repr__(self):
        return f"MPIView({self._parent.__class__.__name__}[{self._start} : {self._stop}] @ Proc {_rank})"


def elapsed_time():
    _comm.Barrier()
    end_time = time.time()
    return end_time - _start_time


def print_elapsed_time(banner="-"):
    etime = elapsed_time()
    if _is_host:
        msg = f"Total elapsed time: {str(timedelta(seconds=etime))}"
        banner = "".join([banner] * len(msg))
        print(f"\n{banner}\n{msg}\n{banner}\n")
