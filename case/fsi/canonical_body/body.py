from pyvicar._utilities import Optional
from pyvicar._tree import Group, Field
from pyvicar._file import Writable
from pyvicar._format import KV1Formatter


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
        self._children.fsi = FSI(f, defaulton=False)

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


class General(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.bodyType = Field("body_type", "unstruc", "", {"unstruc": 4})
        self._children.bodyDim = Field("body_dim", 3)
        self._children.motionType = Field("motionType", "fixed", "", {"fixed": 0})
        self._children.membraneType = Field(
            "membraneType", "open", "", {"open": 1, "closed": 2, "diff": 3}
        )

        self._children.combinedType = Field("combinedType", 0)
        self._children.combinedGroupIndex = Field("combinedGroupIndex", 0)
        self._children.surfaceIntegral = Field(
            "surfaceIntegral", True, "", Field.vmapPresets.bool2int
        )

        self._children.wallType = Field(
            "wallType",
            "noslip_nonporous",
            "",
            {"noslip_nonporous": 0, "slip_porous": 1},
        )

        self._children.nPtsGCMBodyMarker = Field("nPtsGCMBodyMarker", 0)
        self._children.nTriElement = Field("nTriElement", 0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.bodyType
        self._formatter += self._children.bodyDim
        self._formatter += self._children.motionType
        self._formatter += self._children.membraneType
        self._formatter.splittext = "|-general"
        self._formatter.write()
        self._formatter.splittext = " |-"

        self._formatter += self._children.combinedType
        self._formatter += self._children.combinedGroupIndex
        self._formatter += self._children.surfaceIntegral
        self._formatter.write()

        self._formatter += self._children.wallType
        self._formatter.write()

        self._formatter += self._children.nPtsGCMBodyMarker
        self._formatter += self._children.nTriElement
        self._formatter.write()


class Position(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.radiusx = Field("radiusx", 0.0)
        self._children.radiusy = Field("radiusy", 0.0)
        self._children.radiusz = Field("radiusz", 0.0)

        self._children.centx = Field("centx", 0.0)
        self._children.centy = Field("centy", 0.0)
        self._children.centz = Field("centz", 0.0)

        self._children.alpha = Field("alpha", 0.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.radiusx
        self._formatter += self._children.radiusy
        self._formatter += self._children.radiusz
        self._formatter.splittext = "|-position"
        self._formatter.write()
        self._formatter.splittext = " |-"

        self._formatter += self._children.centx
        self._formatter += self._children.centy
        self._formatter += self._children.centz
        self._formatter.write()

        self._formatter += self._children.alpha
        self._formatter.write()


class Motion(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.vxCentTrans = Field("vxCentTrans", 0.0)
        self._children.vyCentTrans = Field("vyCentTrans", 0.0)
        self._children.vzCentTrans = Field("vzCentTrans", 0.0)

        self._children.ampx = Field("ampx", 0.0)
        self._children.ampy = Field("ampy", 0.0)
        self._children.ampz = Field("ampz", 0.0)

        self._children.freqx = Field("freqx", 0.0)
        self._children.freqy = Field("freqy", 0.0)
        self._children.freqz = Field("freqz", 0.0)

        self._children.angvx = Field("angvx", 0.0)
        self._children.angvy = Field("angvy", 0.0)
        self._children.angvz = Field("angvz", 0.0)

        self._children.phase = Field("phase", 0.0)

        self._children.ampangx = Field("ampangx", 0.0)
        self._children.ampangy = Field("ampangy", 0.0)
        self._children.ampangz = Field("ampangz", 0.0)

        self._children.freqangx = Field("freqangx", 0.0)
        self._children.freqangy = Field("freqangy", 0.0)
        self._children.freqangz = Field("freqangz", 0.0)

        self._children.iFixed = Field("iFixed", 0)
        self._children.fixedMotherBody = Field("fixedMotherBody", 0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.vxCentTrans
        self._formatter += self._children.vyCentTrans
        self._formatter += self._children.vzCentTrans
        self._formatter.splittext = "|-motion"
        self._formatter.write()
        self._formatter.splittext = " |-"

        self._formatter += self._children.ampx
        self._formatter += self._children.ampy
        self._formatter += self._children.ampz
        self._formatter.write()

        self._formatter += self._children.freqx
        self._formatter += self._children.freqy
        self._formatter += self._children.freqz
        self._formatter.write()

        self._formatter += self._children.angvx
        self._formatter += self._children.angvy
        self._formatter += self._children.angvz
        self._formatter.write()

        self._formatter += self._children.phase
        self._formatter.write()

        self._formatter += self._children.ampangx
        self._formatter += self._children.ampangy
        self._formatter += self._children.ampangz
        self._formatter.write()

        self._formatter += self._children.freqangx
        self._formatter += self._children.freqangy
        self._formatter += self._children.freqangz
        self._formatter.write()

        self._formatter += self._children.iFixed
        self._formatter += self._children.fixedMotherBody
        self._formatter.write()


class WallPorousVelocity(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.mMinWallVelocity = Field("mMinWallVelocity", 0)
        self._children.mMaxWallVelocity = Field("mMaxWallVelocity", 0)

        self._children.ampVelX = Field("ampVelX", 0.0)
        self._children.ampVelY = Field("ampVelY", 0.0)
        self._children.ampVelZ = Field("ampVelZ", 0.0)

        self._children.freqVelX = Field("freqVelX", 0.0)
        self._children.freqVelY = Field("freqVelY", 0.0)
        self._children.freqVelZ = Field("freqVelZ", 0.0)

        self._children.phaseVelX = Field("phaseVelX", 0.0)
        self._children.phaseVelY = Field("phaseVelY", 0.0)
        self._children.phaseVelZ = Field("phaseVelZ", 0.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.mMinWallVelocity
        self._formatter += self._children.mMaxWallVelocity
        self._formatter.splittext = "|-porous"
        self._formatter.write()
        self._formatter.splittext = " |-"

        self._formatter += self._children.ampVelX
        self._formatter += self._children.ampVelY
        self._formatter += self._children.ampVelZ
        self._formatter.write()

        self._formatter += self._children.freqVelX
        self._formatter += self._children.freqVelY
        self._formatter += self._children.freqVelZ
        self._formatter.write()

        self._formatter += self._children.phaseVelX
        self._formatter += self._children.phaseVelY
        self._formatter += self._children.phaseVelZ
        self._formatter.write()


class Material(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.densityFluid = Field("densityFluid", 1.0)
        self._children.densitySolid = Field("densitySolid", 100.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.densityFluid
        self._formatter += self._children.densitySolid
        self._formatter.splittext = "|-material"
        self._formatter.write()
        self._formatter.splittext = " |-"


class RestoringForce(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.xcentConstR = Field("xcentConstR", 0.0)
        self._children.ycentConstR = Field("ycentConstR", 0.0)
        self._children.zcentConstR = Field("zcentConstR", 0.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.xcentConstR
        self._formatter += self._children.ycentConstR
        self._formatter += self._children.zcentConstR
        self._formatter.splittext = "|-restrForce"
        self._formatter.write()
        self._formatter.splittext = " |-"


class FSI(Group, Writable, Optional):
    def __init__(self, f, defaulton=False):
        Optional.__init__(self, defaulton)
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV1Formatter(f)

        self._children.youngsMod = Field("youngsMod", 1000.0)
        self._children.thickness = Field("thickness", 0.01)
        self._children.damping = Field("damping", 0.0)
        self._children.nu = Field("nu", 0.4)
        self._children.vmass = Field("vmass", 0.0)
        self._children.GMod = Field("GMod", 4.032e-3)

        self._children.forceOpt = Field("forceOpt", 1)
        self._children.dirichletBCOpt = Field("dirichletBCOpt", 0)

        self._children.forceX = Field("forceX", 0)
        self._children.forceY = Field("forceY", 0)
        self._children.forceZ = Field("forceZ", 0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.youngsMod
        self._formatter += self._children.thickness
        self._formatter += self._children.damping
        self._formatter += self._children.nu
        self._formatter += self._children.vmass
        self._formatter += self._children.GMod
        self._formatter.splittext = "|-fsi"
        self._formatter.write()
        self._formatter.splittext = " |-"

        self._formatter += self._children.forceOpt
        self._formatter += self._children.dirichletBCOpt
        self._formatter.write()

        self._formatter += self._children.forceX
        self._formatter += self._children.forceY
        self._formatter += self._children.forceZ
        self._formatter.write()
