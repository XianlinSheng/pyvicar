from pathlib import Path
from pyvicar.tree.group import Group
from pyvicar.file.io import Writable
from .nodes import Nodes
from .markers import Markers


class Probe(Group, Writable):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)
        self._path = Path(path)
        self._f = open(self._path, 'w')

        # all subgroups
        self._children.nodes = Nodes(self._f)
        self._children.markers = Markers(self._f)

        self._finalize_init()
   

    def write(self):
        f = self._f

        self._children.nodes.write()

        f.write('\n')

        self._children.markers.write()

