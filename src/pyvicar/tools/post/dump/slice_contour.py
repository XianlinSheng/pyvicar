import pyvista as pv
import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi
from . import labels as lb
from pyvicar.tools.miscellaneous import args
from .preprocesses.data import prep_field, get_vtks_markers, dispatch_styles
from .preprocesses.conversions import normal_to_plane, resolution_to_size
from dataclasses import dataclass
from collections.abc import Iterable


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


@dataclass
class Vec3:
    xyz: list

    @classmethod
    def from_iterable(cls, obj):
        if not isinstance(obj, Iterable):
            raise TypeError(f"Vec3 must be an Iterable, got {obj}")

        if len(obj) != 3:
            raise ValueError(f"Vec3 must have length 3, got {len(obj)}, {obj}")

        return Vec3(list(obj))

    @classmethod
    def from_iterable_or_vec3(cls, obj):
        if isinstance(obj, Vec3):
            return Vec3(obj.xyz)
        else:
            return Vec3.from_iterable(obj)

    # this means obj can be [x, y, z] or [[x1, y1, z1], [x2, y2, z2]]
    # [x, y, z] -> Vec3(x, y, z)
    # [[x1, ...], [x2, ...]] -> [Vec3(x1, ...), Vec3(x2, ...)]
    @classmethod
    def from_iterable_list(cls, obj):
        if isinstance(obj, Vec3):
            return obj

        if not isinstance(obj, Iterable):
            raise TypeError(
                f"Vec3 must at least be an Iterable in any cases, got {obj}"
            )

        n = len(obj)

        veclist = False
        if n != 3 or isinstance(obj[0], Iterable) or isinstance(obj[0], Vec3):
            veclist = True

        if veclist:
            return [Vec3.from_iterable_or_vec3(vec) for vec in obj]
        else:
            return Vec3.from_iterable_or_vec3(obj)


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
    contour_kwargs={},
    marker_color=lb.Color.uniform("white"),
    marker_texture=lb.Texture.none(),
    marker_opacity=1,
    marker_kwargs={},
    show_outline=False,
    add_axes=False,
    show_grid=False,
    enable_anti_aliasing=False,
    keep_frames=True,
    resolution="4k",
    out_name="vel",
):
    lb.assert_label(contour_color, "contour_color", lb.ColorBase, iterable=True)
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

    c, vtks, markers = get_vtks_markers(c, vtks, markers)

    # this wraps the [x, y, z] as a Vec3 object to distinguish list for compact dump
    # [x, y, z] MUST BE IN FULL, BROADCAST NOT ALLOWED, OTHERWISE IMPOSSIBLE TO DISTINGUISH
    origin = Vec3.from_iterable_list(origin)

    styles = dispatch_styles(
        out_name,
        a=a,
        # these arguments at function call can be lists for compact rendering
        normal=normal,
        origin=origin,
        clip=clip,
        marker_f=marker_f,
        plotter_f=plotter_f,
        origin_f=origin_f,
        clip_f=clip_f,
        contour_color=contour_color,
        contour_kwargs=contour_kwargs,
        marker_color=marker_color,
        marker_texture=marker_texture,
        marker_opacity=marker_opacity,
        marker_kwargs=marker_kwargs,
        show_outline=show_outline,
        add_axes=add_axes,
        show_grid=show_grid,
        enable_anti_aliasing=enable_anti_aliasing,
        keep_frames=keep_frames,
        resolution=resolution,
    )

    for style in styles:
        if style.origin_f is None:
            style.origin_f = lambda c, i, v, m: origin

        if style.clip_f is None:
            style.clip_f = lambda c, i, v, m: clip

    mpi.set_async()

    for i, (vtk, marker) in mpi.dispatch(enumerate(zip(vtks, markers))):
        log.log(
            f"Slice Contour Video: Posting frame {i} {vtk}{f' with {marker}' if marker is not None else ''}"
        )

        mesh = vtk.to_pyvista()

        if marker is not None:
            bodies = marker.to_pyvista_multiblocks()

        mesh = mesh.cell_data_to_point_data(pass_cell_data=False)

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

            if isinstance(style.contour_color, lb.ColorField):
                mesh = prep_field(mesh, style.contour_color.field)

            origin_t = style.origin_f(c, i, vtk, marker)
            if isinstance(origin_t, Vec3):
                origin_t = origin_t.xyz
            clip_t = style.clip_f(c, i, vtk, marker)
            slice = create_slice(mesh, style.normal, origin_t, clip_t)
            if slice.n_points == 0 or slice.n_cells == 0:
                log.log(f"Slice Contour Video: Empty slice")
            else:
                plotter.add_mesh(
                    slice,
                    smooth_shading=True,
                    **style.contour_color.add_mesh_kwargs(),
                    **style.contour_kwargs,
                )

            # looking at the positive side, normal points to camera
            plotter.camera_position = normal_to_plane(style.normal)
            # plotter.camera.ParallelProjectionOn()
            # plotter.camera.zoom(1.5)

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
        a.frames.to_video(outformat="mp4")
        if not keep_frames:
            del a.frames
        mpi.barrier()
        a.read()  # update the new video

        return a
