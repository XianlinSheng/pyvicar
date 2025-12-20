from pathlib import Path
from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV1Formatter
from .bodies import Bodies


axisMap = {"aligned": 0, "x": 1, "y": 2, "z": 3}


class CanonicalBody(Group, Writable):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)
        self._path = Path(path)
        self._f = open(self._path, "w")
        self._headerFormatter = KV1Formatter(self._f)

        self._children.nBody = Field("nBody", 0)
        self._children.nBodySolid = Field("nBodySolid", 0)
        self._children.nBodyMembrane = Field("nBodyMembrane", 0)

        self._children.bodies = Bodies(self._f)

        self._children.iBodyFrameX = Field("iBodyFrameX", "aligned", "", axisMap)
        self._children.iBodyFrameY = Field("iBodyFrameY", "aligned", "", axisMap)
        self._children.iBodyFrameZ = Field("iBodyFrameZ", "aligned", "", axisMap)

        self._finalize_init()

    def write(self):
        f = self._f

        self._headerFormatter += self._children.nBody
        self._headerFormatter += self._children.nBodySolid
        self._headerFormatter += self._children.nBodyMembrane
        self._headerFormatter.write()

        f.write("\n")

        self._children.bodies.write()

        self._headerFormatter += self._children.iBodyFrameX
        self._headerFormatter += self._children.iBodyFrameY
        self._headerFormatter += self._children.iBodyFrameZ
        self._headerFormatter.write()

        f.flush()
