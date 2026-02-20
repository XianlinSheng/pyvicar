import pyvista as pv
import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi
from . import labels as lb
from pyvicar.tools.miscellaneous import args
from .preprocesses.data import prep_field, get_vtks_markers
from .preprocesses.conversions import normal_to_plane, resolution_to_size


# make the slice contour
def create_slice(
    mesh,
    normal="z",
    origin=[None, None, None],
    clip=None,  # [x1, x2, y1, y2, z1, z2]
):
    x1, x2, y1, y2, z1, z2 = mesh.bounds
    origin = args.none_to_default(origin, [(x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2])
    slice = mesh.slice(origin=origin, normal=normal)
    if clip is not None:
        clip = args.none_to_default(clip, [x1, x2, y1, y2, z1, z2])
        slice = slice.clip_box(clip, invert=False)

    return slice


# quick generate
def create_slicecontour_video(
    c,
    vtks,
    markers=None,
    normal="z",
    origin=[None, None, None],
    clip=None,
    marker_f=lambda c, i, v, m: m,
    plotter_f=lambda p, c, i, v, m: p,
    origin_f=None,
    clip_f=None,
    contour_color=lb.Color.field(lb.Field.vector("VEL")),
    marker_opacity=1,
    keep_frames=True,
    resolution="4k",
    out_name="vel",
):
    if not isinstance(contour_color, lb.ColorBase):
        raise TypeError(
            f"Use Color wizard to create argument, but encounter {type(contour_color)}"
        )

    c.post.enable()
    c.post.animations.enable()
    a = c.post.animations.get_or_create(out_name)
    a.frames.enable()

    c, vtks, markers = get_vtks_markers(c, vtks, markers)

    if origin_f is None:
        origin_f = lambda c, i, v, m: origin

    if clip_f is None:
        clip_f = lambda c, i, v, m: clip

    mpi.set_async()

    for i, (vtk, marker) in mpi.dispatch(enumerate(zip(vtks, markers))):
        log.log(
            f"Slice Contour Video: Posting frame {i} {vtk}{f' with {marker}' if marker is not None else ''}"
        )

        mesh = vtk.to_pyvista()
        mesh = mesh.cell_data_to_point_data(pass_cell_data=False)
        plotter = pv.Plotter(off_screen=True)

        if marker is not None:
            bodies = marker.to_pyvista_multiblocks()
            bodies = marker_f(c, i, vtk, bodies)
            for body in bodies:
                plotter.add_mesh(body, opacity=marker_opacity)

        if isinstance(contour_color, lb.ColorField):
            mesh, field_name = prep_field(mesh, contour_color.field)

        origin_t = origin_f(c, i, vtk, marker)
        clip_t = clip_f(c, i, vtk, marker)
        slice = create_slice(mesh, normal, origin_t, clip_t)
        if slice.n_points == 0 or slice.n_cells == 0:
            log.log(f"Slice Contour Video: Empty slice")
        else:
            match contour_color:
                case lb.ColorUniform():
                    plotter.add_mesh(
                        slice,
                        color=contour_color.name,
                        smooth_shading=True,
                    )
                case lb.ColorField():
                    plotter.add_mesh(
                        slice,
                        scalars=field_name,
                        cmap=contour_color.cmap,
                        clim=contour_color.clim,
                        show_scalar_bar=True,
                        scalar_bar_args=contour_color.scalar_bar_args,
                        smooth_shading=True,
                    )

        # looking at the positive side, normal points to camera
        plotter.camera_position = normal_to_plane(normal)
        # plotter.camera.ParallelProjectionOn()
        # plotter.camera.zoom(1.5)
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
