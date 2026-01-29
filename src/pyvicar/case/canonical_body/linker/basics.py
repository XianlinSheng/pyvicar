from pathlib import Path
from pyvicar._format import KV1Formatter
from pyvicar._tree import Field
from pyvicar.tools.miscellaneous import args
from pyvicar.case.canonical_body.bodies import Bodies


class BasicsLinker:
    __version__ = "1.0"

    @staticmethod
    def def_path(self, path):
        self._path = Path(path)
        self._f = open(self._path, "w")
        self._headerFormatter = KV1Formatter(self._f)

    _default_children = {
        "nbody": True,
        "bodies": True,
    }

    @staticmethod
    def def_children(self, def_list={}, config={}):
        def_list = args.add_default(def_list, BasicsLinker._default_children)

        if def_list["nbody"]:
            self._children.nBody = Field("nBody", 0)
            self._children.nBodySolid = Field("nBodySolid", 0)
            self._children.nBodyMembrane = Field("nBodyMembrane", 0)

        if def_list["bodies"]:
            self._children.bodies = Bodies(self._f, config=config)

    @staticmethod
    def write_children(self, def_list={}):
        def_list = args.add_default(def_list, BasicsLinker._default_children)

        f = self._f

        if def_list["nbody"]:
            self._headerFormatter += self._children.nBody
            self._headerFormatter += self._children.nBodySolid
            self._headerFormatter += self._children.nBodyMembrane
            self._headerFormatter.write()
            f.write("\n")

        if def_list["bodies"]:
            self._children.bodies.write()
