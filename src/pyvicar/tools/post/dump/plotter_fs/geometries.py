import numpy as np
import pyvista as pv
import pyvicar.tools.fp as fp
from pyvicar.tools.post.dump.preprocesses.conversions import vecstr_to_array


def make_plane_plotter_f(
    xyz_f,
    normal_f,
    color="black",
    opacity_f=fp.uniform_f(0.2),
    size_f=fp.uniform_f((5, 5)),
):
    def plotter_f(plotter, c, i, v, m):
        xyz_t = xyz_f(c, i, v, m)
        normal_t = vecstr_to_array(normal_f(c, i, v, m))
        opacity_t = opacity_f(c, i, v, m)
        size_t = size_f(c, i, v, m)
        plane = pv.Plane(
            center=xyz_t,
            direction=normal_t,
            i_size=size_t[0],
            j_size=size_t[1],
        )
        plotter.add_mesh(plane, color=color, opacity=opacity_t)
        return plotter

    return plotter_f


def make_curve_plotter_f(xyzs_f, color="black", line_width=5):
    def plotter_f(plotter, c, i, v, m):
        xyzs = np.asarray(xyzs_f(c, i, v, m))
        curve = pv.lines_from_points(xyzs)
        plotter.add_mesh(curve, color=color, line_width=line_width)
        return plotter

    return plotter_f


def make_cube_plotter_f(xyz_f, a_f, color="black", opacity_f=fp.uniform_f(1)):
    def plotter_f(plotter, c, i, v, m):
        xyz = xyz_f(c, i, v, m)
        a = a_f(c, i, v, m)
        opacity_t = opacity_f(c, i, v, m)
        cube = pv.Cube(center=xyz, x_length=a[0], y_length=a[1], z_length=a[2])
        plotter.add_mesh(cube, color=color, opacity=opacity_t)
        return plotter

    return plotter_f


def make_polyline_plotter_f(xyz_fs, color="black", line_width=5):
    def plotter_f(plotter, c, i, v, m):
        xyzs = np.array([xyz_f(c, i, v, m) for xyz_f in xyz_fs])
        curve = pv.lines_from_points(xyzs)
        plotter.add_mesh(curve, color=color, line_width=line_width)
        return plotter

    return plotter_f
