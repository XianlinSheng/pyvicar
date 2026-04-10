from pyvicar._tree import Group
from pyvicar.file import Writable
from .linker.basics import BasicsLinker


class Input(Group, Writable):
    def __init__(self, path, def_list={}, config={}):
        Group.__init__(self)
        Writable.__init__(self)

        BasicsLinker.def_path(self, path)

        BasicsLinker.def_children(self, def_list=def_list, config=config)

        self._finalize_init()

    def write(self):
        f = self._f

        BasicsLinker.write_children(self)

        f.flush()
