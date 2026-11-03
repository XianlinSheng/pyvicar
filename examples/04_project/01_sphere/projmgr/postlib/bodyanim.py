import pyvicar

pyvicar.assert_api_version("1.0.2", "1.1.0")

import pyvicar.tools.post.dump.labels as lb
import pyvicar.tools.post.dump.plotter_fs as pf
import pyvicar.tools.fp as fp
import pyvicar.tools.log as log
import numpy as np
from .misc import pflib as pflib

mpi_async = False


def post_bodyanim(p):
    p2 = pflib.make_post_pfs(p)

    c = p.Case(p.name)

    c.dump.read()

    # CASE CHECK: the frames to post
    markers = c.dump.marker
    # markers = c.dump.marker.latest
    # markers = c.dump.marker[::10]

    # CASE CHECK: coloring of q iso surfaces
    iso_color = lb.Color.field(lb.Field.scalar("P"), clim=[-1.0, 0.5], cmap="viridis")
    # iso_color = lb.Color.field(lb.Field.vector("VEL", "z"), clim=[-0.5, 0.5], cmap="viridis")
    # iso_color = lb.Color.field(lb.Field.vector("VEL", "mag"), clim=[0, 1.5], cmap="viridis")

    # CASE CHECK: output name
    outname = "body"

    bodyanim_common_kwargs = {
        "markers": markers,
        "marker_color": lb.Color.uniform("gray"),
        "marker_opacity": 1.0,
        "marker_texture": lb.Texture.specular(),
        "add_axes": False,
        "show_grid": False,
        "keep_frames": False,
    }

    # oclocks = [1, 3, 5, 6, 7, 9, 11, 12]
    oclocks = [1, 3, 5, 7, 9, 11]

    center = p.gm.center + np.array([0, p.span / 4, 0])

    cam_common_kwargs = {
        "target": center,
        "l0": p.span,
        "downstream_shift": 0.5 * p.chord / p.span,
    }

    for oclock in oclocks:
        log.log_host(f"Post Body Anim: Angle {oclock} o clock")
        c.create_bodyanim_video(
            plotter_f=fp.pipeline_f(
                pf.set_cam_compass(
                    pitch=45,
                    oclock=oclock,
                    r=4,
                    **cam_common_kwargs,
                ),
                *p2.area_fs,
            ),
            out_name=f"{outname}_o{oclock}",
            **bodyanim_common_kwargs,
        )

    log.log_host(f"Post Body Anim: Top")
    c.create_bodyanim_video(
        plotter_f=fp.pipeline_f(
            pf.set_cam_compass(
                pitch=90,
                oclock=3,
                r=8,
                **cam_common_kwargs,
            ),
            *p2.area_fs,
        ),
        out_name=f"{outname}_top",
        **bodyanim_common_kwargs,
    )
