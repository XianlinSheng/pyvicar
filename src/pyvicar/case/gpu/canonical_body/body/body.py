from pyvicar._tree import Group
from pyvicar.file import Writable
from pyvicar._format import KV1Formatter
from pyvicar.case.common.canonical_body.body.general import General
from pyvicar.case.common.canonical_body.body.position import Position
from pyvicar.case.common.canonical_body.body.motion import Motion
from .fsi import FSI
from pyvicar.case.common.canonical_body.body.wall_porous import WallPorousVelocity
from pyvicar.case.common.canonical_body.body.material import Material
from pyvicar.case.common.canonical_body.body.restoring_force import RestoringForce


class Body(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.general = General(
            f,
            extMotionTypes={},
        )
        self._children.position = Position(f)
        self._children.motion = Motion(f)
        self._children.fsi = FSI(f, defaulton=False)
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
        if self._children.fsi:
            self._children.fsi.write()
