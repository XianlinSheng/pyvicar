from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter, write_banner

pbcTypes = {"dirichlet": 1, "neumann": 2}


class PressureBoundaryConditions(Group):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)
        self._f = f

        self._children.x1 = X1(f)
        self._children.x2 = X2(f)
        self._children.y1 = Y1(f)
        self._children.y2 = Y2(f)
        self._children.z1 = Z1(f)
        self._children.z2 = Z2(f)

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


class X1(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.pbcx1 = Field("pbcx1", "neumann", "", pbcTypes)
        self._children.pppx1 = Field("pppx1", 0.0)
        self._children.userFlag = Field(
            "userFlag", False, "", Field.vmapPresets.bool2int
        )

        self._finalize_init()

    def write(self):
        self._formatter += self._children.pbcx1
        self._formatter += self._children.pppx1
        self._formatter += self._children.userFlag
        self._formatter.write()


class X2(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.pbcx2 = Field("pbcx2", "neumann", "", pbcTypes)
        self._children.pppx2 = Field("pppx2", 0.0)
        self._children.userFlag = Field(
            "userFlag", False, "", Field.vmapPresets.bool2int
        )

        self._finalize_init()

    def write(self):
        self._formatter += self._children.pbcx2
        self._formatter += self._children.pppx2
        self._formatter += self._children.userFlag
        self._formatter.write()


class Y1(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.pbcy1 = Field("pbcy1", "neumann", "", pbcTypes)
        self._children.pppy1 = Field("pppy1", 0.0)
        self._children.userFlag = Field(
            "userFlag", False, "", Field.vmapPresets.bool2int
        )

        self._finalize_init()

    def write(self):
        self._formatter += self._children.pbcy1
        self._formatter += self._children.pppy1
        self._formatter += self._children.userFlag
        self._formatter.write()


class Y2(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.pbcy2 = Field("pbcy2", "neumann", "", pbcTypes)
        self._children.pppy2 = Field("pppy2", 0.0)
        self._children.userFlag = Field(
            "userFlag", False, "", Field.vmapPresets.bool2int
        )

        self._finalize_init()

    def write(self):
        self._formatter += self._children.pbcy2
        self._formatter += self._children.pppy2
        self._formatter += self._children.userFlag
        self._formatter.write()


class Z1(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.pbcz1 = Field("pbcz1", "neumann", "", pbcTypes)
        self._children.pppz1 = Field("pppz1", 0.0)
        self._children.userFlag = Field(
            "userFlag", False, "", Field.vmapPresets.bool2int
        )

        self._finalize_init()

    def write(self):
        self._formatter += self._children.pbcz1
        self._formatter += self._children.pppz1
        self._formatter += self._children.userFlag
        self._formatter.write()


class Z2(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.pbcz2 = Field("pbcz2", "neumann", "", pbcTypes)
        self._children.pppz2 = Field("pppz2", 0.0)
        self._children.userFlag = Field(
            "userFlag", False, "", Field.vmapPresets.bool2int
        )

        self._finalize_init()

    def write(self):
        self._formatter += self._children.pbcz2
        self._formatter += self._children.pppz2
        self._formatter += self._children.userFlag
        self._formatter.write()
