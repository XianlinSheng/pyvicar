from pyvicar._tree import Group, Field
from pyvicar._file import Writable
from pyvicar._format import KV1Formatter


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
