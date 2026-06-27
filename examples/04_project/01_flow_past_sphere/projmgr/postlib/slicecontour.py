import pyvicar
import pyvicar.tools.post.dump.labels as lb
import pyvicar.tools.post.dump.plotter_fs as pf
import pyvicar.tools.log as log

pyvicar.assert_api_version("1.0.1", "1.1.0")

mpi_async = False


def post_slicecontour(p):
    c = p.Case(p.name)

    c.dump.read()

    # CASE CHECK: the frames to post
    vtks, markers = c.dump.vtm, c.dump.marker
    # vtks, markers = c.dump.vtm.latest, c.dump.marker.latest
    # vtks, markers = c.dump.vtm[::10], c.dump.marker[::10]

    # CASE CHECK: fields to plot
    colors = {
        "vor": lb.Color.field(
            lb.Field.vor_from_vel("VEL", "y"),
            clim=[-0.1, 0.1],
            cmap="coolwarm",
        ),
        "p": lb.Color.field(
            lb.Field.scalar("P"),
            clim=[-0.5, 0.5],
            cmap="coolwarm",
        ),
        "vel": lb.Color.field(
            lb.Field.vector("VEL", "mag"),
            clim=[0, 1.5],
            cmap="coolwarm",
        ),
    }

    # CASE CHECK: output name, consider the field for coloring
    outname = "slice"

    # CASE CHECK: slice orientation and position
    normal = "y"
    origin = [None, None, None]

    for field, color in colors.items():
        log.log_host(f"Post Contour: {field}")
        c.create_slicecontour_video(
            vtks,
            markers,
            normal=normal,
            origin=origin,
            contour_color=color,
            marker_color=lb.Color.uniform("white"),
            marker_opacity=1,
            marker_texture=lb.Texture.specular(),
            plotter_f=pf.set_cam_compass(
                p.gm.center,
                l0=p.d,
                r=10,
                # CASE CHECK: needs to be compatible with slice orientation
                oclock=3,
                pitch=0,
                downstream_shift=2,
            ),
            add_axes=False,
            show_outline=False,
            show_grid=False,
            enable_anti_aliasing=True,
            keep_frames=False,
            out_name=f"{outname}_{field}",
        )
