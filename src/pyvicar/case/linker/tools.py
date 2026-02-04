import pyvicar.tools.physics_setter.common as phys
import pyvicar.geometry.case_setter.common as geom
import pyvicar.grid.case_setter.common as grid
from pyvicar.grid.previewer.common import show_grid, stat_grid
from pyvicar.tools.post.case_setter.common import create_matplotlib_fig
from pyvicar.tools.post.dump import create_isoq_video, create_slicecontour_video


class ToolsLinker:
    __version__ = "1.0"

    @staticmethod
    def link(cls):
        cls.set_inlet = phys.set_inlet
        cls.set_re = phys.set_re
        cls.stat_tstep = phys.stat_tstep
        cls.stat_viscosity = phys.stat_viscosity

        cls.append_solid = geom.append_solid
        cls.append_solid_2d = geom.append_solid_2d
        cls.append_sphere = geom.append_sphere
        cls.append_cyl_2d = geom.append_cyl_2d
        cls.append_stl_solid = geom.append_stl_solid
        cls.append_npz_solid_2d = geom.append_npz_solid_2d
        cls.append_membrane = geom.append_membrane
        cls.append_plane = geom.append_plane
        cls.append_stl_membrane = geom.append_stl_membrane
        cls.append_ib2_membrane = geom.append_ib2_membrane

        cls.refine_grid = grid.refine_grid
        cls.uniform_grid_n = grid.uniform_grid_n
        cls.uniform_grid_dx = grid.uniform_grid_dx
        cls.grid_2d = grid.grid_2d
        cls.apply_grid_model = grid.apply_grid_model
        cls.create_grid = grid.create_grid

        cls.show_grid = show_grid
        cls.stat_grid = stat_grid

        cls.create_matplotlib_fig = create_matplotlib_fig
        cls.create_isoq_video = create_isoq_video
        cls.create_slicecontour_video = create_slicecontour_video

        return cls
