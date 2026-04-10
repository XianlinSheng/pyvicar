from pyvicar._tree import Group
from pyvicar.file import Writable
from .linker import BasicsLinker


class Body(Group, Writable):
    def __init__(self, f, config):
        Group.__init__(self)
        Writable.__init__(self)

        BasicsLinker.def_file(self, f)

        BasicsLinker.def_children(self, config=config)

        self._finalize_init()

    def write(self):
        BasicsLinker.write_children(self)
