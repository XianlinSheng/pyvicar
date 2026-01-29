from pyvicar._format import KV1Formatter
from pyvicar.case.canonical_body.body.general import General
from pyvicar.case.canonical_body.body.position import Position
from pyvicar.case.canonical_body.body.motion import Motion
from pyvicar.case.canonical_body.body.wall_porous import WallPorousVelocity
from pyvicar.case.canonical_body.body.material import Material
from pyvicar.case.canonical_body.body.restoring_force import RestoringForce
from pyvicar.tools.miscellaneous import args


class BasicsLinker:
    __version__ = "1.0"

    @staticmethod
    def def_file(self, f):
        self._formatter = KV1Formatter(f)
        self._f = f

    _default_children = {
        "general": True,
        "position": True,
        "motion": True,
        "porous": True,
        "material": True,
        "restrForce": True,
    }

    @staticmethod
    def def_children(self, def_list={}, config={}):
        def_list = args.add_default(def_list, BasicsLinker._default_children)
        config = args.add_default(config, {"general": {}})

        f = self._f

        if def_list["general"]:
            self._children.general = General(
                f,
                config=config["general"],
            )

        if def_list["position"]:
            self._children.position = Position(f)

        if def_list["motion"]:
            self._children.motion = Motion(f)

        if def_list["porous"]:
            self._children.porous = WallPorousVelocity(f)

        if def_list["material"]:
            self._children.material = Material(f)

        if def_list["restrForce"]:
            self._children.restrForce = RestoringForce(f)

    @staticmethod
    def write_children(self, def_list={}):
        def_list = args.add_default(def_list, BasicsLinker._default_children)

        if def_list["general"]:
            self._children.general.write()

        if def_list["position"]:
            self._children.position.write()

        if def_list["motion"]:
            self._children.motion.write()

        if def_list["porous"]:
            self._children.porous.write()

        if def_list["material"]:
            self._children.material.write()

        if def_list["restrForce"]:
            self._children.restrForce.write()
