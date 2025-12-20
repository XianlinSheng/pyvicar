from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV1Formatter


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

        self._children.phasex = Field("phasex", 0.0)
        self._children.phasey = Field("phasey", 0.0)
        self._children.phasez = Field("phasez", 0.0)

        self._children.angvx = Field("angvx", 0.0)
        self._children.angvy = Field("angvy", 0.0)
        self._children.angvz = Field("angvz", 0.0)

        self._children.ampangx = Field("ampangx", 0.0)
        self._children.ampangy = Field("ampangy", 0.0)
        self._children.ampangz = Field("ampangz", 0.0)

        self._children.freqangx = Field("freqangx", 0.0)
        self._children.freqangy = Field("freqangy", 0.0)
        self._children.freqangz = Field("freqangz", 0.0)

        self._children.phaseangx = Field("phaseangx", 0.0)
        self._children.phaseangy = Field("phaseangy", 0.0)
        self._children.phaseangz = Field("phaseangz", 0.0)

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

        self._formatter += self._children.phasex
        self._formatter += self._children.phasey
        self._formatter += self._children.phasez
        self._formatter.write()

        self._formatter += self._children.angvx
        self._formatter += self._children.angvy
        self._formatter += self._children.angvz
        self._formatter.write()

        self._formatter += self._children.ampangx
        self._formatter += self._children.ampangy
        self._formatter += self._children.ampangz
        self._formatter.write()

        self._formatter += self._children.freqangx
        self._formatter += self._children.freqangy
        self._formatter += self._children.freqangz
        self._formatter.write()

        self._formatter += self._children.phaseangx
        self._formatter += self._children.phaseangy
        self._formatter += self._children.phaseangz
        self._formatter.write()
