import pyvista as pv
import numpy as np
from dataclasses import dataclass
from enum import Enum
import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi


class Q:
    def use_exist(q_name):
        return QExist(q_name)

    def from_vel(vel_name="VEL"):
        return QFromVel(vel_name)


@dataclass
class QExist(Q):
    q_name: str


@dataclass
class QFromVel(Q):
    vel_name: str


# make the contour mesh
def create_isoq(
    mesh,
    q=Q.from_vel(),
    iso_value=0.1,
):
    if not isinstance(q, Q):
        raise TypeError(f"Use Q wizard to create argument, but encounter {type(q)}")

    mesh = mesh.cell_data_to_point_data(pass_cell_data=False)

    match q:
        case QExist():
            if q.q_type == FieldType.Cell:
                mesh = cell_to_point(mesh)
            qfield = mesh.point_data[q.q_name]
        case QFromVel():
            mesh = mesh.compute_derivative(q.vel_name, gradient=True)
            grad = mesh.point_data[f"gradient"]
            grad = grad.reshape(-1, 3, 3)  # 3x3 tensor
            gradt = np.transpose(grad, (0, 2, 1))
            S = 0.5 * (grad + gradt)
            Omega = 0.5 * (grad - gradt)
            # Q = 0.5 (‖Ω‖² - ‖S‖²)
            qfield = 0.5 * (
                np.einsum("ijk,ijk->i", Omega, Omega) - np.einsum("ijk,ijk->i", S, S)
            )

    mesh.point_data["Q"] = qfield

    return mesh.contour(isosurfaces=[iso_value], scalars="Q")


class Color:
    def uniform(name="turquoise"):
        return ColorUniform(name)

    def field(
        field_name,
        cmap="viridis",
        clim=None,
        scalar_bar_args=None,
    ):
        return ColorField(field_name, cmap, clim, scalar_bar_args)


@dataclass
class ColorUniform(Color):
    name: str


@dataclass
class ColorField(Color):
    field_name: str
    cmap: str
    clim: None | list
    scalar_bar_args: None | dict


# quick generate
def gen_isoq_video(
    vtklist,
    markers=None,
    marker_f=lambda m: m,
    plotter_f=lambda p: p,
    iso_opacity=0.5,
    iso_color=Color.uniform(),
    keep_frames=True,
):
    c = vtklist.case
    c.post.enable()
    c.post.animations.enable()
    a = c.post.animations.get_or_create("q")
    a.frames.enable()

    if not vtklist:
        return a

    mpi.set_async()

    if markers is None:
        markers = [None] * len(vtklist)

    for vtk, marker in mpi.dispatch(zip(vtklist, markers)):
        log.log(
            f"plot_isoq: posting frame {vtk}{f' with {marker}' if marker is not None else ''}"
        )

        mesh = vtk.to_pyvista()
        plotter = pv.Plotter(off_screen=True)

        if marker is not None:
            bodies = marker.to_pyvista_multiblocks()
            bodies = marker_f(bodies)
            for body in bodies:
                plotter.add_mesh(body)

        contours = create_isoq(mesh)
        if contours.n_points == 0 or contours.n_cells == 0:
            log.log(f"plot_isoq: No q isosurfaces after calculation")
        else:
            match iso_color:
                case ColorUniform():
                    plotter.add_mesh(
                        contours,
                        color=iso_color.name,
                        opacity=iso_opacity,
                    )
                case ColorField():
                    plotter.add_mesh(
                        contours,
                        scalars=iso_color.field_name,
                        cmap=iso_color.cmap,
                        clim=iso_color.clim,
                        show_scalar_bar=True,
                        opacity=iso_opacity,
                        scalar_bar_args=iso_color.scalar_bar_args,
                    )

        outline = mesh.outline()
        plotter.add_mesh(outline, color="black", line_width=1)
        plotter.add_axes()
        plotter.show_grid()

        plotter = plotter_f(plotter)

        a.frames.frame_by_pyvista(vtk.seriesi, plotter, window_size=[3840, 2160])

        plotter.close()
        plotter.deep_clean()
        del plotter

        pv.close_all()

    mpi.set_sync()

    a.read()
    mpi.barrier()
    a = c.post.animations["q"]
    a.frames.to_video(outformat="mp4")
    if not keep_frames:
        del a.frames
    mpi.barrier()

    return a
