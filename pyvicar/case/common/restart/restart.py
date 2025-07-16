from pyvicar._tree import Group
from pyvicar.file import Readable
from pyvicar._utilities import Optional
from .flow import FlowLists
from .body import BodyLists


class Restart(Group, Readable, Optional):
    def __init__(self, case):
        Group.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._case = case
        self._path = case.path / "Restart"

        self._children.flow = FlowLists(case)
        self._children.body = BodyLists(case)

        self._finalize_init()

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    def read(self):
        self._children.flow.read()
        self._children.body.read()
        if self._children.flow or self._children.body:
            self._enable()

    @property
    def path(self):
        return self._path

    def to_restart_in(self, tidx=None):
        def tidx_to_attr(obj):
            if tidx is None:
                return obj.latest
            elif tidx == 1:
                return obj.t1
            elif tidx == 2:
                return obj.t2
            else:
                raise ValueError(
                    f"Time idx must be 1, 2, or None (latest), default None"
                )

        if not self:
            raise Exception(f"No active restart files")

        if self._children.flow:
            flowlist = tidx_to_attr(self._children.flow)
            if not flowlist:
                raise ValueError(f"Restart flow out has no given time idx {tidx}")
            flowlist.to_restart_in()

        if self._children.body:
            bodylist = tidx_to_attr(self._children.body)
            if not bodylist:
                raise ValueError(f"Restart body out has no given time idx {tidx}")
            bodylist.to_restart_in()
