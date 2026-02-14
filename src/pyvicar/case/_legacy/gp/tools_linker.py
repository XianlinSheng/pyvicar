from pyvicar.case.common.tools_linker import link_common_tools
from pyvicar.tools.thrombosis.case_setter.gp import set_thrombosis_vars


def link_gp_tools(cls):
    cls = link_common_tools(cls)
    cls.set_thrombosis_vars = set_thrombosis_vars
    return cls
