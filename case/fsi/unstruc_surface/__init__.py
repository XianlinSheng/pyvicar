from pathlib import Path
from pyvicar.utilities import Optional
from pyvicar.tree.group import Group
from pyvicar.file.io import Writable
from pyvicar.tree.field import Field, Point3D
from pyvicar.file.formatter import DatasetFormatter
from .surfaces import Surfaces


class UnstrucSurface(Group, Writable, Optional):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)
        Optional.__init__(self)
        self._path = Path(path)
        if self:
            self._init()


    def _init(self):
        self._f = open(self._path, 'w')
        self._formatter = DatasetFormatter(self._f)

        self._children.fluidPoint = Field('fluidPoint', Point3D([0, 0, 0]))
        self._children.surfaces = Surfaces(self._f)

        self._finalize_init()


    def enable(self):
        Optional.enable(self)
        self._init()


    def write(self):
        if not self:
            raise Exception(f'The object is not active, call .enable() to enable it')

        f = self._f

        f.write('\n')

        for surface in self._children.surfaces:
            surface.write()
            # This is the requirement of the input format
            self._formatter += self._children.fluidPoint
            self._formatter.write()

