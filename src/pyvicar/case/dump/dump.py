from pyvicar._tree import Group
from pyvicar.file import Readable
from .vtk import VTMList, VTKList, VTRList
from .marker import MarkerList


class Dump(Group, Readable):
    def __init__(self, case):
        Group.__init__(self)
        Readable.__init__(self)
        self._case = case

        self._children.vtm = VTMList(case)
        self._children.vtk = VTKList(case)
        self._children.vtr = VTRList(case)
        self._children.marker = MarkerList(case)

        self._finalize_init()

    def read(self):
        self._children.vtm.read()
        self._children.vtk.read()
        self._children.vtr.read()
        self._children.marker.read()
