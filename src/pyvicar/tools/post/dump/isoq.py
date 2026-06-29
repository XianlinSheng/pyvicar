import pyvista as pv
import numpy as np
from dataclasses import dataclass
import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi
from . import labels as lb
from .preprocesses.data import prep_field, get_vtks_markers, dispatch_styles
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
    iso_value=0.1,
    iso_opacity=0.5,
    iso_color=lb.Color.field(lb.Field.vector("VEL")),
    iso_texture=lb.Texture.none(),
    iso_kwargs={},
    marker_opacity=1,
    marker_color=lb.Color.uniform("white"),
    marker_texture=lb.Texture.none(),
    marker_kwargs={},
    show_outline=True,
    add_axes=True,
    show_grid=True,
    enable_anti_aliasing=False,
    keep_frames=True,
    resolution="4k",
    out_name="q",
):
    lb.assert_label(iso_color, "iso_color", lb.ColorBase, iterable=True)
    lb.assert_label(marker_color, "marker_color", lb.ColorBase, iterable=True)

    c.post.enable()
    c.post.animations.enable()
    if isinstance(out_name, list):
        a = [c.post.animations.get_or_create(name) for name in out_name]
        for a1 in a:
            a1.frames.enable()
    else:
        a = c.post.animations.get_or_create(out_name)
        a.frames.enable()

    styles = dispatch_styles(
        out_name,
        a=a,
        # these arguments at function call can be lists for compact rendering
        marker_f=marker_f,
        plotter_f=plotter_f,
        iso_opacity=iso_opacity,
        iso_color=iso_color,
        iso_texture=iso_texture,
        iso_kwargs=iso_kwargs,
        marker_opacity=marker_opacity,
        marker_color=marker_color,
        marker_texture=marker_texture,
        marker_kwargs=marker_kwargs,
        show_outline=show_outline,
        add_axes=add_axes,
        show_grid=show_grid,
        enable_anti_aliasing=enable_anti_aliasing,
        keep_frames=keep_frames,
        resolution=resolution,
    )

    c, vtks, markers = get_vtks_markers(c, vtks, markers)

    mpi.set_async()

    for i, (vtk, marker) in mpi.dispatch(enumerate(zip(vtks, markers))):
        log.log(
            f"ISOQ Video: Posting frame {i} {vtk}{f' with {marker}' if marker is not None else ''}"
        )

        mesh = vtk.to_pyvista()

        if marker is not None:
            bodies = marker.to_pyvista_multiblocks()

        if q_name is None:
            contours = create_isoq(mesh, iso_value=iso_value)
        else:
            contours = create_isoq(mesh, q=Q.use_exist(q_name), iso_value=iso_value)

        if contours.n_points == 0 or contours.n_cells == 0:
            log.log(f"ISOQ Video: No q isosurfaces after calculation")
            continue

        for style in styles:
            plotter = pv.Plotter(off_screen=True)

            if marker is not None:
                bodies = style.marker_f(c, i, vtk, bodies)
                for body in bodies:

                    if isinstance(style.marker_color, lb.ColorField):
                        body = prep_field(body, style.marker_color.field)

                    plotter.add_mesh(
                        body,
                        opacity=style.marker_opacity,
                        smooth_shading=True,
                        **style.marker_color.add_mesh_kwargs(),
                        **style.marker_texture.add_mesh_kwargs(),
                        **style.marker_kwargs,
                    )

            if isinstance(style.iso_color, lb.ColorField):
                contours = prep_field(contours, style.iso_color.field)

            plotter.add_mesh(
                contours,
                opacity=style.iso_opacity,
                smooth_shading=True,
                **style.iso_color.add_mesh_kwargs(),
                **style.iso_texture.add_mesh_kwargs(),
                **style.iso_kwargs,
            )

            if style.show_outline:
                outline = mesh.outline()
                plotter.add_mesh(outline, color="black", line_width=1)
            if style.add_axes:
                plotter.add_axes()
            if style.show_grid:
                plotter.show_grid()
            if style.enable_anti_aliasing:
                plotter.enable_anti_aliasing()

            plotter = style.plotter_f(plotter, c, i, vtk, marker)

            style.a.frames.frame_by_pyvista(
                i,
                plotter,
                window_size=resolution_to_size(style.resolution),
            )

            plotter.close()
            plotter.deep_clean()
            del plotter

        pv.close_all()

    mpi.set_sync()

    if isinstance(out_name, list):
        for style in styles:
            style.a.read()
            mpi.barrier()
            style.a.frames.to_video(outformat="mp4")
            if not style.keep_frames:
                del style.a.frames
            mpi.barrier()
            style.a.read()  # update the new video

        return [style.a for style in styles]

    else:
        a.read()
        mpi.barrier()
        # a = c.post.animations[out_name]
        a.frames.to_video(outformat="mp4")
        if not keep_frames:
            del a.frames
        mpi.barrier()
        a.read()  # update the new video

        return a
