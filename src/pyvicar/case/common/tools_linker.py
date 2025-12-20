from pyvicar.tools.bcic_setter.common import set_inlet
import pyvicar.geometry.case_setter.common as geom
import pyvicar.grid.case_setter.common as grid
from pyvicar.grid.previewer.common import show_grid


def link_common_tools(cls):
    cls.set_inlet = set_inlet
    cls.append_solid = geom.append_solid
    cls.append_solid_2d = geom.append_solid_2d
    cls.append_sphere = geom.append_sphere
    cls.append_cyl_2d = geom.append_cyl_2d
    cls.refine_grid = grid.refine_grid
    cls.uniform_grid_n = grid.uniform_grid_n
    cls.uniform_grid_dx = grid.uniform_grid_dx
    cls.grid_2d = grid.grid_2d
    cls.apply_grid_model = grid.apply_grid_model
    cls.grid_default = grid.grid_default
    cls.show_grid = show_grid
    return cls
