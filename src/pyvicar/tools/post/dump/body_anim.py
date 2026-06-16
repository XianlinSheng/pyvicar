import pyvista as pv
import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi
from . import labels as lb
from .preprocesses.data import prep_field
from .preprocesses.conversions import resolution_to_size


# quick generate
# (c, i, v, m) is fixed plotter function arguments, 
# v(vtk) is always set None when called in this case
def create_bodyanim_video(
    c,
    markers=None,
    marker_f=lambda c, i, v, m: m,
    plotter_f=lambda p, c, i, v, m: p,
    marker_opacity=1,
    marker_color=lb.Color.uniform("white"),
    marker_texture=lb.Texture.none(),
    marker_kwargs={},
    add_axes=True,
    show_grid=True,
    enable_anti_aliasing=False,
    keep_frames=True,
    resolution="4k",
    out_name="q",
):
    if markers is None:
        c.dump.marker.read()
        if c.dump.marker:
            markers = c.dump.marker.latest
        else:
            raise Exception(
                f"Create Video: No Marker available, or pass Marker list by markers=..."
            )

    if not isinstance(marker_color, lb.ColorBase):
        raise TypeError(
            f"Use Color wizard to create argument, got {type(marker_color)} for marker_color"
        )

    c.post.enable()
    c.post.animations.enable()
    a = c.post.animations.get_or_create(out_name)
    a.frames.enable()

    mpi.set_async()

    for i, marker in mpi.dispatch(enumerate(markers)):
        log.log(
            f"Body Anim Video: Posting frame {i} {marker}"
        )

        plotter = pv.Plotter(off_screen=True)

        bodies = marker.to_pyvista_multiblocks()
        bodies = marker_f(c, i, None, bodies)
        for body in bodies:

            if isinstance(marker_color, lb.ColorField):
                body = prep_field(body, marker_color.field)

            plotter.add_mesh(
                body,
                opacity=marker_opacity,
                smooth_shading=True,
                **marker_color.add_mesh_kwargs(),
                **marker_texture.add_mesh_kwargs(),
                **marker_kwargs,
            )

        if add_axes:
            plotter.add_axes()
        if show_grid:
            plotter.show_grid()
        if enable_anti_aliasing:
            plotter.enable_anti_aliasing()

        plotter = plotter_f(plotter, c, i, None, marker)

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

    a.read()  # update the new video

    return a
