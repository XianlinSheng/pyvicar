from pyvicar._tree import Group
from pyvicar.file import Writable, Readable
from pyvicar.case.linker.tools import ToolsLinker
from pyvicar.case.linker.basics import BasicsLinker


@ToolsLinker.link_addons()
@ToolsLinker.link()
@BasicsLinker.def_methods()
class Case(Group, Writable, Readable):
    def __init__(self, path="."):
        Group.__init__(self)
        Writable.__init__(self)
        Readable.__init__(self)

        BasicsLinker.def_path(self, path)

        BasicsLinker.def_children(
            self,
            restart_configs=[
                {"prefix": "flow"},
                {"prefix": "body"},
            ],
        )

        self._finalize_init()

    def write(self):
        BasicsLinker.write_children(self)

    def read(self):
        BasicsLinker.read_children(self)
