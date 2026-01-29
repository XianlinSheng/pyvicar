from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter, write_banner
from pyvicar.tools.miscellaneous import args


class BoundaryConditions(Group):
    def __init__(self, f, config={}):
        Group.__init__(self)
        Writable.__init__(self)

        config = args.add_default(
            config,
            {
                "bc_types": {
                    "default": "neumann",
                    "vmap": {"dirichlet": 1, "neumann": 2, "symmetry": 4},
                }
            },
            recursive=True,
        )

        self._formatter = KV2Formatter(f)
        self._f = f

        self._children.x1 = BC1(f, "x1", config)
        self._children.x2 = BC1(f, "x2", config)
        self._children.y1 = BC1(f, "y1", config)
        self._children.y2 = BC1(f, "y2", config)
        self._children.z1 = BC1(f, "z1", config)
        self._children.z2 = BC1(f, "z2", config)

        self._finalize_init()

    def write(self):
        f = self._f

        write_banner(f, "Left Boundary (x1)", length=48, filler="-")
        self._children.x1.write()

        write_banner(f, "Right Boundary (x2)", length=48, filler="-")
        self._children.x2.write()

        write_banner(f, "Bottom Boundary (y1)", length=48, filler="-")
        self._children.y1.write()

        write_banner(f, "Top Boundary (y2)", length=48, filler="-")
        self._children.y2.write()

        write_banner(f, "Front Boundary (z1)", length=48, filler="-")
        self._children.z1.write()

        write_banner(f, "Back Boundary (z2)", length=48, filler="-")
        self._children.z2.write()


class BC1(Group, Writable):
    def __init__(self, f, pos, config):
        Group.__init__(self)
        Writable.__init__(self)

        self._formatter = KV2Formatter(f)

        self._pos = pos

        def set_children(children, name, *args):
            setattr(children, name, Field(name, *args))

        def set_children_config(children, name, config):
            setattr(children, name, Field(name, config["default"], "", config["vmap"]))

        set_children_config(self._children, f"bc{pos}", config["bc_types"])

        for dir in ["u", "v", "w"]:
            set_children(self._children, f"{dir}{pos}", 0.0)
            set_children(self._children, f"freq{dir}{pos}", 0.0)

        set_children(self._children, f"beta{pos}", 0.0)

        self._finalize_init()

    def write(self):
        pos = self._pos

        self._formatter += getattr(self._children, f"bc{pos}")
        for dir in ["u", "v", "w"]:
            self._formatter += getattr(self._children, f"{dir}{pos}")
        for dir in ["u", "v", "w"]:
            self._formatter += getattr(self._children, f"freq{dir}{pos}")
        self._formatter += getattr(self._children, f"beta{pos}")
        self._formatter.write()
