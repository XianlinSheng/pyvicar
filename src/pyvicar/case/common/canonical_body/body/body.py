from pyvicar._tree import Group
from pyvicar.file import Writable
from pyvicar._format import KV1Formatter
from .general import General
from .position import Position
from .motion import Motion
from .wall_porous import WallPorousVelocity
from .material import Material
from .restoring_force import RestoringForce


def add_basics(body_children, f, extMotionTypes={}):
    body_children.general = General(f, extMotionTypes)
    body_children.position = Position(f)
    body_children.motion = Motion(f)
    body_children.porous = WallPorousVelocity(f)
    body_children.material = Material(f)
    body_children.restrForce = RestoringForce(f)

    return body_children


def write_basics(body_children):
    body_children.general.write()
    body_children.position.write()
    body_children.motion.write()
    body_children.porous.write()
    body_children.material.write()
    body_children.restrForce.write()


class Body(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)
        self._f = f

        add_basics(self._children, self._f)

        self._finalize_init()

    def write(self):
        write_basics(self._children)
