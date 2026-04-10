from pathlib import Path
from pyvicar._tree import Group, Field
from pyvicar._utilities import Optional
from pyvicar.file import Writable
from pyvicar._format import KV2Formatter, write_banner


class Thrombosis(Group, Writable, Optional):
    def __init__(self, path):
        Group.__init__(self)
        Writable.__init__(self)
        Optional.__init__(self)
        self._path = Path(path)
        if self:
            self._init()

    def _init(self):
        self._f = open(self._path, "w")
        self._headerFormatter = KV2Formatter(self._f)

        self._children.scaling = Scaling(self._f)
        self._children.varMap = VarMap(self._f)
        self._children.permeability = Permeability(self._f)
        self._children.reaction = Reaction(self._f)

        self._finalize_init()

    def enable(self):
        Optional.enable(self)
        self._init()

    def write(self):
        if not self:
            raise Exception(f"The object is not active, call .enable() to enable it")

        f = self._f

        write_banner(f, "Scaling (scaling)")
        self._children.scaling.write()

        write_banner(f, "Variable Mapping (varMap)")
        self._children.varMap.write()

        write_banner(f, "Permeability (permeability)")
        self._children.permeability.write()

        write_banner(f, "Reaction Rates (reaction)")
        self._children.reaction.write()

        f.flush()


class Scaling(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.len = Field("len", 1.0)
        self._children.time = Field("time", 1.0)

        self._finalize_init()

    def write(self):
        self._formatter += self._children.len
        self._formatter += self._children.time
        self._formatter.write()


class VarMap(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.iCPT = Field("iCPT", 1, "Prothrombin")
        self._children.iCTH = Field("iCTH", 2, "Thrombin")
        self._children.iCAT = Field("iCAT", 3, "Anti-Thrombin")

        self._children.iCFG = Field("iCFG", 4, "Fibrinogen")
        self._children.iCFI = Field("iCFI", 5, "Fibrin")

        self._children.iCRP = Field("iCRP", 6, "Rest-PLT")
        self._children.iCAP = Field("iCAP", 7, "Active-PLT")
        self._children.iCBP = Field("iCBP", 8, "Bound-PLT")

        self._children.iRT = Field("iRT", 9, "Residence Time")
        self._children.iTI = Field("iTI", 9, "Thrombus Index")

        self._finalize_init()

    def write(self):
        self._formatter += self._children.iCPT
        self._formatter += self._children.iCTH
        self._formatter += self._children.iCAT
        self._formatter.write()

        self._formatter += self._children.iCFG
        self._formatter += self._children.iCFI
        self._formatter.write()

        self._formatter += self._children.iCRP
        self._formatter += self._children.iCAP
        self._formatter += self._children.iCBP
        self._formatter.write()

        self._formatter += self._children.iRT
        self._formatter += self._children.iTI
        self._formatter.write()


class Permeability(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.kfi = Field("kfi", 1.5e-10, "Darcy coef")
        self._children.cfip50 = Field("cfip50", 3.5e3, "Hill fn 50 coef")
        self._children.nfip = Field("nfip", 4, "Hill fn order")

        self._children.kbp = Field("kbp", 1.5e-11, "Darcy coef")
        self._children.cbpp50 = Field("cbpp50", 1.5e2, "Hill fn 50 coef")
        self._children.nbpp = Field("nbpp", 4, "Hill fn order")

        self._finalize_init()

    def write(self):
        self._formatter += self._children.kfi
        self._formatter += self._children.cfip50
        self._formatter += self._children.nfip
        self._formatter.write()

        self._formatter += self._children.kbp
        self._formatter += self._children.cbpp50
        self._formatter += self._children.nbpp
        self._formatter.write()


class Reaction(Group, Writable):
    def __init__(self, f):
        Group.__init__(self)
        Writable.__init__(self)
        self._formatter = KV2Formatter(f)

        self._children.krpth = Field("krpth", 1e-3)
        self._children.kapth = Field("kapth", 6e-3)
        self._children.kbpth = Field("kbpth", 1e-3)

        self._children.katth = Field("katth", 7e-6)

        self._children.kthfi = Field("kthfi", 5.9e1)
        self._children.kthmfi = Field("kthmfi", 3.16e3)

        self._children.kthpa = Field("kthpa", 5e-1)
        self._children.cthpa50 = Field("cthpa50", 9.11e-1, "Hill fn 50 coef")
        self._children.nthpa = Field("nthpa", 4, "Hill fn order")

        self._children.kappa = Field("kappa", 1e-4)

        self._children.kfipb = Field("kfipb", 1e2)
        self._children.cfipb50 = Field("cfipb50", 6e2, "Hill fn 50 coef")
        self._children.nfipb = Field("nfipb", 2, "Hill fn order")

        self._children.rtpb50 = Field("rtpb50", 5e0, "Hill fn 50 coef")
        self._children.nrtpb = Field("nrtpb", 4, "Hill fn order")

        self._children.srpb50 = Field("srpb50", 2.5e1, "Hill fn 50 coef")
        self._children.nsrpb = Field("nsrpb", 4, "Hill fn order")

        self._finalize_init()

    def write(self):
        self._formatter += self._children.krpth
        self._formatter += self._children.kapth
        self._formatter += self._children.kbpth
        self._formatter.write()

        self._formatter += self._children.katth
        self._formatter.write()

        self._formatter += self._children.kthfi
        self._formatter += self._children.kthmfi
        self._formatter.write()

        self._formatter += self._children.kthpa
        self._formatter += self._children.cthpa50
        self._formatter += self._children.nthpa
        self._formatter.write()

        self._formatter += self._children.kappa
        self._formatter.write()

        self._formatter += self._children.kfipb
        self._formatter += self._children.cfipb50
        self._formatter += self._children.nfipb
        self._formatter.write()

        self._formatter += self._children.rtpb50
        self._formatter += self._children.nrtpb
        self._formatter.write()

        self._formatter += self._children.srpb50
        self._formatter += self._children.nsrpb
        self._formatter.write()
