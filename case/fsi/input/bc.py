from pyvicar._tree import Group, Field
from pyvicar._file import Writable
from pyvicar._format import KV2Formatter, write_banner

bcTypes = {"dirichlet": 1, "neumann": 2, "symmetry": 4}


class BoundaryConditions(Group):
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

        self._children.bcx1 = Field("bcx1", "dirichlet", "", bcTypes)
        self._children.ux1 = Field("ux1", 0.0)
        self._children.vx1 = Field("vx1", 0.0)
        self._children.wx1 = Field("wx1", 0.0)
        self._children.frequx1 = Field("frequx1", 0.0)
        self._children.freqvx1 = Field("freqvx1", 0.0)
        self._children.freqwx1 = Field("freqwx1", 0.0)
        self._children.betax1 = Field("betax1", 0.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.bcx1
        self._formatter += self._children.ux1
        self._formatter += self._children.vx1
        self._formatter += self._children.wx1
        self._formatter += self._children.frequx1
        self._formatter += self._children.freqvx1
        self._formatter += self._children.freqwx1
        self._formatter += self._children.betax1
        self._formatter.write()


class X2(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.bcx2 = Field("bcx2", "dirichlet", "", bcTypes)
        self._children.ux2 = Field("ux2", 0.0)
        self._children.vx2 = Field("vx2", 0.0)
        self._children.wx2 = Field("wx2", 0.0)
        self._children.frequx2 = Field("frequx2", 0.0)
        self._children.freqvx2 = Field("freqvx2", 0.0)
        self._children.freqwx2 = Field("freqwx2", 0.0)
        self._children.betax2 = Field("betax2", 0.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.bcx2
        self._formatter += self._children.ux2
        self._formatter += self._children.vx2
        self._formatter += self._children.wx2
        self._formatter += self._children.frequx2
        self._formatter += self._children.freqvx2
        self._formatter += self._children.freqwx2
        self._formatter += self._children.betax2
        self._formatter.write()


class Y1(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.bcy1 = Field("bcy1", "dirichlet", "", bcTypes)
        self._children.uy1 = Field("uy1", 0.0)
        self._children.vy1 = Field("vy1", 0.0)
        self._children.wy1 = Field("wy1", 0.0)
        self._children.frequy1 = Field("frequy1", 0.0)
        self._children.freqvy1 = Field("freqvy1", 0.0)
        self._children.freqwy1 = Field("freqwy1", 0.0)
        self._children.betay1 = Field("betay1", 0.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.bcy1
        self._formatter += self._children.uy1
        self._formatter += self._children.vy1
        self._formatter += self._children.wy1
        self._formatter += self._children.frequy1
        self._formatter += self._children.freqvy1
        self._formatter += self._children.freqwy1
        self._formatter += self._children.betay1
        self._formatter.write()


class Y2(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.bcy2 = Field("bcy2", "dirichlet", "", bcTypes)
        self._children.uy2 = Field("uy2", 0.0)
        self._children.vy2 = Field("vy2", 0.0)
        self._children.wy2 = Field("wy2", 0.0)
        self._children.frequy2 = Field("frequy2", 0.0)
        self._children.freqvy2 = Field("freqvy2", 0.0)
        self._children.freqwy2 = Field("freqwy2", 0.0)
        self._children.betay2 = Field("betay2", 0.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.bcy2
        self._formatter += self._children.uy2
        self._formatter += self._children.vy2
        self._formatter += self._children.wy2
        self._formatter += self._children.frequy2
        self._formatter += self._children.freqvy2
        self._formatter += self._children.freqwy2
        self._formatter += self._children.betay2
        self._formatter.write()


class Z1(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.bcz1 = Field("bcz1", "dirichlet", "", bcTypes)
        self._children.uz1 = Field("uz1", 0.0)
        self._children.vz1 = Field("vz1", 0.0)
        self._children.wz1 = Field("wz1", 0.0)
        self._children.frequz1 = Field("frequz1", 0.0)
        self._children.freqvz1 = Field("freqvz1", 0.0)
        self._children.freqwz1 = Field("freqwz1", 0.0)
        self._children.betaz1 = Field("betaz1", 0.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.bcz1
        self._formatter += self._children.uz1
        self._formatter += self._children.vz1
        self._formatter += self._children.wz1
        self._formatter += self._children.frequz1
        self._formatter += self._children.freqvz1
        self._formatter += self._children.freqwz1
        self._formatter += self._children.betaz1
        self._formatter.write()


class Z2(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.bcz2 = Field("bcz2", "dirichlet", "", bcTypes)
        self._children.uz2 = Field("uz2", 0.0)
        self._children.vz2 = Field("vz2", 0.0)
        self._children.wz2 = Field("wz2", 0.0)
        self._children.frequz2 = Field("frequz2", 0.0)
        self._children.freqvz2 = Field("freqvz2", 0.0)
        self._children.freqwz2 = Field("freqwz2", 0.0)
        self._children.betaz2 = Field("betaz2", 0.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.bcz2
        self._formatter += self._children.uz2
        self._formatter += self._children.vz2
        self._formatter += self._children.wz2
        self._formatter += self._children.frequz2
        self._formatter += self._children.freqvz2
        self._formatter += self._children.freqwz2
        self._formatter += self._children.betaz2
        self._formatter.write()
