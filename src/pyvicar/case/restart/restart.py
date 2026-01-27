from pyvicar._tree import Group
from pyvicar.file import Readable
from pyvicar._utilities import Optional
from .restart_pack import RestartPackPool


class Restart(Group, Readable, Optional):
    def __init__(self, case, configs):
        Group.__init__(self)
        Readable.__init__(self)
        Optional.__init__(self)
        self._case = case
        self._path = case.path / "Restart"

        for config in configs:
            setattr(
                self._children,
                config["prefix"],
                RestartPackPool(case, config["prefix"]),
            )

        self._finalize_init()

    def _enable(self):
        return super().enable()

    def _disable(self):
        return super().disable()

    def read(self):
        for obj in self._children.values():
            obj.read()
        if any(self._children.values()):
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

        def pool_to_restart_in(obj):
            if obj:
                rpool = tidx_to_attr(obj)
                if not rpool:
                    raise ValueError(
                        f"Restart out pool {obj.prefix} has no given time idx {tidx}"
                    )
                rpool.to_restart_in()

        if not self:
            raise Exception(f"No active restart files")

        for obj in self._children.values():
            pool_to_restart_in(obj)
