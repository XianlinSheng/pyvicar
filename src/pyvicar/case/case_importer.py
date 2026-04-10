from pyvicar.addons_importer import import_addons


def import_case(install_prefix):
    addons_mod, paths = import_addons(install_prefix)

    Case = addons_mod.case.Case

    @property
    def runpath(self):
        return paths.exe

    Case.runpath = runpath

    return Case
