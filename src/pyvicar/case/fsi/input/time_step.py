from pyvicar._tree import Group, Field
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter


class TimeStepControl(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.ntStep = Field("ntSteps", 1)
        self._children.nMonitor = Field("nMonitor", 1)
        self._children.nDump = Field("nDump", 1)
        self._children.nRestart = Field("nRestart", 1)
        self._children.nStat = Field("nStat", 0)
        self._children.nProbe = Field("nProbe", 1)
        self._children.nInit = Field("nInit", 0)
        self._children.nDumpInit = Field("nDumpInit", 0)

        self._children.formatDump = Field(
            "formatDump", "vtk", "", {"rawq": 0, "vtk": 1}
        )
        self._children.iDragLift = Field(
            "iDragLift", True, "", Field.vmapPresets.bool2int
        )
        self._children.iVerbose = Field(
            "iVerbose", False, "", Field.vmapPresets.bool2int
        )

        self._children.re = Field("re", 100.0)
        self._children.dt = Field("dt", 1e-3)
        self._children.fr = Field("fr", 0.0)
        self._children.stopTime = Field("stopTime", 9e99)

        self._children.fracStep = Field(
            "frac_step", "nonvankan", "", {"nonvankan": 0, "vankan": 1}
        )
        self._children.advectionScheme = Field(
            "advection_scheme", "cn2", "", {"ab2": 1, "cn1": 2, "cn2": 3}
        )

        self._finalize_init()

    def write(self):
        self._formatter += self._children.ntStep
        self._formatter += self._children.nMonitor
        self._formatter += self._children.nDump
        self._formatter += self._children.nRestart
        self._formatter += self._children.nStat
        self._formatter += self._children.nProbe
        self._formatter += self._children.nInit
        self._formatter += self._children.nDumpInit
        self._formatter.write()

        self._formatter += self._children.formatDump
        self._formatter += self._children.iDragLift
        self._formatter += self._children.iVerbose
        self._formatter.write()

        self._formatter += self._children.re
        self._formatter += self._children.dt
        self._formatter += self._children.fr
        self._formatter += self._children.stopTime
        self._formatter.write()

        self._formatter += self._children.fracStep
        self._formatter += self._children.advectionScheme
        self._formatter.write()
