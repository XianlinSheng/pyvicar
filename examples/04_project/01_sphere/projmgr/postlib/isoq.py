import pyvicar

pyvicar.assert_api_version("1.0.3", "1.1.0")

import pyvicar.tools.post.dump.labels as lb
import pyvicar.tools.post.dump.plotter_fs as pf
import pyvicar.tools.fp as fp
import pyvicar.tools.log as log
import numpy as np
from .misc import pflib as pflib

mpi_async = False


def post_isoq(p):
    p2 = pflib.make_post_pfs(p)

    c = p.Case(p.name)

    c.dump.read()

    # CASE CHECK: the frames to post
    vtks, markers = c.dump.vtm, c.dump.marker
    # vtks, markers = c.dump.vtm.latest, c.dump.marker.latest
    # vtks, markers = c.dump.vtm[::10], c.dump.marker[::10]

    isoq_common_kwargs = {
        "vtks": vtks,
        "markers": markers,
        # "surf_interp": {"pos": True, "neg": True},
        # "surf_interp_radius": 0.1 * p.chord,
        # CASE CHECK: use the dumpped Q or set as None to auto calc
        "q_name": None,  # "Q",
        "iso_value": 1,
        # "marker_color": lb.Color.uniform("white"),
        # "iso_opacity": 1.0,
        "marker_opacity": 1.0,
        "iso_texture": lb.Texture.specular(),
        "marker_texture": lb.Texture.specular(),
        "add_axes": False,
        "show_outline": False,
        "show_grid": False,
        "keep_frames": False,
    }

    fields = [
        ("p", lb.Color.field(lb.Field.scalar("P"), clim=[-1.0, 0.5], cmap="viridis")),
        (
            "v",
            lb.Color.field(
                lb.Field.vector("VEL", "y"), clim=[-0.5, 0.5], cmap="viridis"
            ),
        ),
    ]

    # oclocks = [1, 3, 5, 6, 7, 9, 11, 12]
    oclocks = [1, 3, 5, 7, 9, 11]

    center = p.gm.center + np.array([0, p.span / 2, 0])

    cam_common_kwargs = {
        "target": center,
        "l0": p.span,
        "downstream_shift": 1,
    }

    plotter_fs = []
    iso_colors = []
    iso_opacities = []
    marker_colors = []
    out_names = []

    for field_name, field_color in fields:
        for oclock in oclocks:
            plotter_fs.append(
                fp.pipeline_f(
                    pf.set_cam_compass(
                        pitch=45,
                        oclock=oclock,
                        r=5,
                        **cam_common_kwargs,
                    ),
                )
            )
            iso_colors.append(field_color)
            iso_opacities.append(1)
            marker_colors.append(lb.Color.uniform("white"))
            out_names.append(f"q_{field_name}_o{oclock}")

            plotter_fs.append(
                fp.pipeline_f(
                    pf.set_cam_compass(
                        pitch=-60,
                        oclock=oclock,
                        r=4,
                        target=center,
                        l0=p.span,
                        downstream_shift=0.5 * p.chord / p.span,
                    ),
                )
            )
            iso_colors.append(field_color)
            iso_opacities.append(1)
            marker_colors.append(lb.Color.uniform("white"))
            out_names.append(f"q_{field_name}_o{oclock}_bel")

        plotter_fs.append(
            fp.pipeline_f(
                pf.set_cam_compass(
                    pitch=90,
                    oclock=3,
                    r=10,
                    **cam_common_kwargs,
                ),
            )
        )
        iso_colors.append(field_color)
        iso_opacities.append(1)
        marker_colors.append(lb.Color.uniform("white"))
        out_names.append(f"q_{field_name}_top")

        plotter_fs.append(
            fp.pipeline_f(
                pf.set_cam_compass(
                    pitch=-90,
                    oclock=3,
                    r=10,
                    **cam_common_kwargs,
                ),
            )
        )
        iso_colors.append(field_color)
        iso_opacities.append(1)
        marker_colors.append(lb.Color.uniform("white"))
        out_names.append(f"q_{field_name}_bel")

    # # below plots far view and a mirror/copy of the surface with pressure contour distribution

    # cam_common_kwargs = {
    #     "target": p2.mirror_center,
    #     "l0": p.span,
    #     "downstream_shift": 1,
    # }

    # for oclock in oclocks:
    #     plotter_fs.append(
    #         fp.pipeline_f(
    #             p2.mirror_wing_f,
    #             pf.set_cam_compass(
    #                 pitch=30,
    #                 r=6,
    #                 oclock=oclock,
    #                 **cam_common_kwargs,
    #             ),
    #         )
    #     )
    #     iso_colors.append(field_color)
    #     iso_opacities.append(1)
    #     marker_colors.append(lb.Color.uniform("white"))
    #     out_names.append(f"q_{field_name}_far_surf_o{oclock}")

    # plotter_fs.append(
    #     fp.pipeline_f(
    #         p2.mirror_wing_f,
    #         pf.set_cam_compass(
    #             pitch=90,
    #             r=18,
    #             oclock=3,
    #             **cam_common_kwargs,
    #         ),
    #     )
    # )
    # iso_colors.append(field_color)
    # iso_opacities.append(1)
    # marker_colors.append(lb.Color.uniform("white"))
    # out_names.append(f"q_{field_name}_far_surf_top")

    # plotter_fs.append(
    #     fp.pipeline_f(
    #         pf.set_cam_compass(
    #             pitch=90,
    #             oclock=3,
    #             r=8,
    #             l0=p.span,
    #             target=p.gm.center + [p.chord / 2, p.chord, 0],
    #             downstream_shift=0,
    #         ),
    #     )
    # )
    # iso_colors.append(lb.Color.uniform("white"))
    # marker_colors.append(
    #     lb.Color.field(
    #         lb.Field.compute_scalar(
    #             "DP",
    #             ["P(SURF_POS)", "P(SURF_NEG)"],
    #             lambda pos, neg: neg - pos,
    #         ),
    #         clim=[-1, 1],
    #     )
    # )
    # iso_opacities.append(0)
    # out_names.append(f"dp_top")

    c.create_isoq_video(
        iso_color=iso_colors,
        iso_opacity=iso_opacities,
        marker_color=marker_colors,
        plotter_f=plotter_fs,
        out_name=out_names,
        **isoq_common_kwargs,
    )
