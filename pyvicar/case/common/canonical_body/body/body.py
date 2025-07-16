from pyvicar._tree import Group
from pyvicar.file import Writable
from pyvicar._format import KV1Formatter
from .general import General
from .position import Position
from .motion import Motion
from .wall_porous import WallPorousVelocity
from .material import Material
from .restoring_force import RestoringForce


class Body(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.general = General(f)
        self._children.position = Position(f)
        self._children.motion = Motion(f)
        self._children.porous = WallPorousVelocity(f)
        self._children.material = Material(f)
        self._children.restrForce = RestoringForce(f)

        self._finalize_init()

    def write(self):
        self._children.general.write()
        self._children.position.write()
        self._children.motion.write()
        self._children.porous.write()
        self._children.material.write()
        self._children.restrForce.write()
