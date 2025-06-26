from pathlib import Path
from pyvicar._tree import Group, List, Field
from pyvicar._file import Writable
from pyvicar._format import KV1Formatter


class RHM(Group, Writable):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)
        self._path = Path(path)
        if self:
            self._init()

    def _init(self):
        self._f = open(self._path, "w")
        self._headerFormatter = KV1Formatter(self._f)

        self._children.rhmRestart = Field(
            "rhmRestart", False, "", Field.vmapPresets.bool2int
        )
        self._children.nRHMBody = Field("nRHMBody", 0)

        self._children.bodies = RHMBodies(self._f)

        self._finalize_init()

    def write(self):
        if not self:
            raise Exception(f"The object is not active, call .enable() to enable it")

        f = self._f

        self._headerFormatter += self._children.rhmRestart
        self._headerFormatter += self._children.nRHMBody
        self._headerFormatter.write()

        f.write("\n")

        self._children.bodies.write()

        f.flush()


class RHMBodies(List, Writable):
    def __init__(self, f):
        List.__init__(self)
        Writable.__init__(self)
        self._f = f

    def _elemcheck(self, new):
        if not isinstance(new, RHMBody):
            raise TypeError(f"Expected an RHMBody object, but encountered {repr(new)}")

    def write(self):
        f = self._f

        for body in self:
            body.write()
            f.write("\n")

    def appendnew(self, n=1):
        newobjs = [RHMBody(self._f) for _ in range(n)]
        self._childrenlist += newobjs
        if n == 1:
            return newobjs[0]
        else:
            return newobjs

    def resetnew(self, n=1):
        self._childrenlist = [RHMBody(self._f) for _ in range(n)]


class RHMBody(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.iBody = Field("iBody", 0)

        self._children.restrictNeg = Field(
            "restrictNeg", False, "", Field.vmapPresets.bool2int
        )
        self._children.restrictPos = Field(
            "restrictPos", False, "", Field.vmapPresets.bool2int
        )

        self._children.restrictNegXOffset = Field("restrictNegXOffset", 0.0)
        self._children.restrictNegYOffset = Field("restrictNegYOffset", 0.0)
        self._children.restrictNegZOffset = Field("restrictNegZOffset", 0.0)
        self._children.restrictPosXOffset = Field("restrictPosXOffset", 0.0)
        self._children.restrictPosYOffset = Field("restrictPosYOffset", 0.0)
        self._children.restrictPosZOffset = Field("restrictPosZOffset", 0.0)
        self._children.kx = Field("kx", 0.0)
        self._children.ky = Field("ky", 0.0)
        self._children.kz = Field("kz", 0.0)
        self._children.cx = Field("cx", 0.0)
        self._children.cy = Field("cy", 0.0)
        self._children.cz = Field("cz", 0.0)
        self._children.k0_xoffset = Field("k0_xoffset", 0.0)
        self._children.k0_yoffset = Field("k0_yoffset", 0.0)
        self._children.k0_zoffset = Field("k0_zoffset", 0.0)

        self._children.xcentBody = Field("xcentBody", 0.0)
        self._children.ycentBody = Field("ycentBody", 0.0)
        self._children.zcentBody = Field("zcentBody", 0.0)
        self._children.xcentBase = Field("xcentBase", 0.0)
        self._children.ycentBase = Field("ycentBase", 0.0)
        self._children.zcentBase = Field("zcentBase", 0.0)

        self._children.angxBody = Field("angxBody", 0.0)
        self._children.angyBody = Field("angyBody", 0.0)
        self._children.angzBody = Field("angzBody", 0.0)
        self._children.angxBase = Field("angxBase", 0.0)
        self._children.angyBase = Field("angyBase", 0.0)
        self._children.angzBase = Field("angzBase", 0.0)

        self._children.vxcentBase = Field("vxcentBase", 0.0)
        self._children.vycentBase = Field("vycentBase", 0.0)
        self._children.vzcentBase = Field("vzcentBase", 0.0)

        self._children.ampxBase = Field("ampxBase", 0.0)
        self._children.ampyBase = Field("ampyBase", 0.0)
        self._children.ampzBase = Field("ampzBase", 0.0)

        self._children.freqxBase = Field("freqxBase", 0.0)
        self._children.freqyBase = Field("freqyBase", 0.0)
        self._children.freqzBase = Field("freqzBase", 0.0)

        self._children.phasexBase = Field("phasexBase", 0.0)
        self._children.phaseyBase = Field("phaseyBase", 0.0)
        self._children.phasezBase = Field("phasezBase", 0.0)

        self._children.angvxBase = Field("angvxBase", 0.0)
        self._children.angvyBase = Field("angvyBase", 0.0)
        self._children.angvzBase = Field("angvzBase", 0.0)

        self._children.ampangxBase = Field("ampangxBase", 0.0)
        self._children.ampangyBase = Field("ampangyBase", 0.0)
        self._children.ampangzBase = Field("ampangzBase", 0.0)

        self._children.freqangxBase = Field("freqangxBase", 0.0)
        self._children.freqangyBase = Field("freqangyBase", 0.0)
        self._children.freqangzBase = Field("freqangzBase", 0.0)

        self._children.phaseangxBase = Field("phaseangxBase", 0.0)
        self._children.phaseangyBase = Field("phaseangyBase", 0.0)
        self._children.phaseangzBase = Field("phaseangzBase", 0.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.iBody
        self._formatter.write()

        self._formatter += self._children.restrictNeg
        self._formatter += self._children.restrictPos
        self._formatter.write()

        self._formatter += self._children.restrictNegXOffset
        self._formatter += self._children.restrictNegYOffset
        self._formatter += self._children.restrictNegZOffset
        self._formatter.write()

        self._formatter += self._children.restrictPosXOffset
        self._formatter += self._children.restrictPosYOffset
        self._formatter += self._children.restrictPosZOffset
        self._formatter.write()

        self._formatter += self._children.kx
        self._formatter += self._children.ky
        self._formatter += self._children.kz
        self._formatter.write()

        self._formatter += self._children.cx
        self._formatter += self._children.cy
        self._formatter += self._children.cz
        self._formatter.write()

        self._formatter += self._children.k0_xoffset
        self._formatter += self._children.k0_yoffset
        self._formatter += self._children.k0_zoffset
        self._formatter.write()

        self._formatter += self._children.xcentBody
        self._formatter += self._children.ycentBody
        self._formatter += self._children.zcentBody
        self._formatter.write()

        self._formatter += self._children.xcentBase
        self._formatter += self._children.ycentBase
        self._formatter += self._children.zcentBase
        self._formatter.write()

        self._formatter += self._children.angxBody
        self._formatter += self._children.angyBody
        self._formatter += self._children.angzBody
        self._formatter.write()

        self._formatter += self._children.angxBase
        self._formatter += self._children.angyBase
        self._formatter += self._children.angzBase
        self._formatter.write()

        self._formatter += self._children.vxcentBase
        self._formatter += self._children.vycentBase
        self._formatter += self._children.vzcentBase
        self._formatter.write()

        self._formatter += self._children.ampxBase
        self._formatter += self._children.ampyBase
        self._formatter += self._children.ampzBase
        self._formatter.write()

        self._formatter += self._children.freqxBase
        self._formatter += self._children.freqyBase
        self._formatter += self._children.freqzBase
        self._formatter.write()

        self._formatter += self._children.phasexBase
        self._formatter += self._children.phaseyBase
        self._formatter += self._children.phasezBase
        self._formatter.write()

        self._formatter += self._children.angvxBase
        self._formatter += self._children.angvyBase
        self._formatter += self._children.angvzBase
        self._formatter.write()

        self._formatter += self._children.ampangxBase
        self._formatter += self._children.ampangyBase
        self._formatter += self._children.ampangzBase
        self._formatter.write()

        self._formatter += self._children.freqangxBase
        self._formatter += self._children.freqangyBase
        self._formatter += self._children.freqangzBase
        self._formatter.write()

        self._formatter += self._children.phaseangxBase
        self._formatter += self._children.phaseangyBase
        self._formatter += self._children.phaseangzBase
        self._formatter.write()
