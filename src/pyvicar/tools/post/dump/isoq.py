import pyvista as pv
import numpy as np
from dataclasses import dataclass
import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi
from . import labels as lb
from .preprocesses.data import prep_field, get_vtks_markers
from .preprocesses.conversions import resolution_to_size


class QBase:
    pass


@dataclass
class QExist(QBase):
    q_name: str


@dataclass
class QFromVel(QBase):
    vel_name: str


class Q:
    def use_exist(q_name):
        return QExist(q_name)

    def from_vel(vel_name="VEL"):
        return QFromVel(vel_name)


# make the contour mesh
def create_isoq(
    mesh,
    q=Q.from_vel(),
    iso_value=0.1,
):
    if not isinstance(q, QBase):
        raise TypeError(f"Use Q wizard to create argument, but encounter {type(q)}")

    mesh = mesh.cell_data_to_point_data(pass_cell_data=False)

    match q:
        case QExist():
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


# quick generate
def create_isoq_video(
    c,
    vtks=None,
    markers=None,
    q_name=None,
    marker_f=lambda c, i, v, m: m,
    plotter_f=lambda p, c, i, v, m: p,
    iso_opacity=0.5,
    iso_color=lb.Color.field(lb.Field.vector("VEL")),
    marker_opacity=1,
    keep_frames=True,
    resolution="4k",
    out_name="q",
):
    if not isinstance(iso_color, lb.ColorBase):
        raise TypeError(
            f"Use Color wizard to create argument, but encounter {type(iso_color)}"
        )

    c.post.enable()
    c.post.animations.enable()
    a = c.post.animations.get_or_create(out_name)
    a.frames.enable()

    c, vtks, markers = get_vtks_markers(c, vtks, markers)

    mpi.set_async()

    for i, (vtk, marker) in mpi.dispatch(enumerate(zip(vtks, markers))):
        log.log(
            f"ISOQ Video: Posting frame {i} {vtk}{f' with {marker}' if marker is not None else ''}"
        )

        mesh = vtk.to_pyvista()
        plotter = pv.Plotter(off_screen=True)

        if marker is not None:
            bodies = marker.to_pyvista_multiblocks()
            bodies = marker_f(c, i, vtk, bodies)
            for body in bodies:
                plotter.add_mesh(body, opacity=marker_opacity)

        if q_name is None:
            contours = create_isoq(mesh)
        else:
            contours = create_isoq(mesh, q=Q.use_exist(q_name))

        if contours.n_points == 0 or contours.n_cells == 0:
            log.log(f"ISOQ Video: No q isosurfaces after calculation")
        else:
            match iso_color:
                case lb.ColorUniform():
                    plotter.add_mesh(
                        contours,
                        color=iso_color.name,
                        opacity=iso_opacity,
                        smooth_shading=True,
                    )
                case lb.ColorField():
                    contours, field_name = prep_field(contours, iso_color.field)
                    plotter.add_mesh(
                        contours,
                        scalars=field_name,
                        cmap=iso_color.cmap,
                        clim=iso_color.clim,
                        show_scalar_bar=True,
                        opacity=iso_opacity,
                        scalar_bar_args=iso_color.scalar_bar_args,
                        smooth_shading=True,
                    )

        outline = mesh.outline()
        plotter.add_mesh(outline, color="black", line_width=1)
        plotter.add_axes()
        plotter.show_grid()

        plotter = plotter_f(plotter, c, i, vtk, marker)

        a.frames.frame_by_pyvista(
            i,
            plotter,
            window_size=resolution_to_size(resolution),
        )

        plotter.close()
        plotter.deep_clean()
        del plotter

        pv.close_all()

    mpi.set_sync()

    a.read()
    mpi.barrier()
    a = c.post.animations[out_name]
    a.frames.to_video(outformat="mp4")
    if not keep_frames:
        del a.frames
    mpi.barrier()

    return a
