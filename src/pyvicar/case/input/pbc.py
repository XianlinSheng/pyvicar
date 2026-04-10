from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter, write_banner
from pyvicar.tools.miscellaneous import args


class PressureBoundaryConditions(Group):
    def __init__(self, f, config={}):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)
        self._f = f

        config = args.add_default(
            config,
            {
                "pbc_types": {
                    "default": "neumann",
                    "vmap": {"dirichlet": 1, "neumann": 2},
                }
            },
            recursive=True,
        )

        self._children.x1 = PBC1(f, "x1", config)
        self._children.x2 = PBC1(f, "x2", config)
        self._children.y1 = PBC1(f, "y1", config)
        self._children.y2 = PBC1(f, "y2", config)
        self._children.z1 = PBC1(f, "z1", config)
        self._children.z2 = PBC1(f, "z2", config)

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


class PBC1(Group, Writable):
    def __init__(self, f, pos, config):
        Group.__init__(self)
        Writable.__init__(self)

        self._formatter = KV2Formatter(f)

        self._pos = pos

        def set_children(children, name, *args):
            setattr(children, name, Field(name, *args))

        def set_children_config(children, name, config):
            setattr(children, name, Field(name, config["default"], "", config["vmap"]))

        set_children_config(self._children, f"pbc{pos}", config["pbc_types"])
        set_children(self._children, f"ppp{pos}", 0.0)
        set_children(self._children, f"iUser", False, "", Field.vmapPresets.bool2int)

        self._finalize_init()

    def write(self):
        pos = self._pos

        self._formatter += getattr(self._children, f"pbc{pos}")
        self._formatter += getattr(self._children, f"ppp{pos}")
        self._formatter += getattr(self._children, f"iUser")
        self._formatter.write()
