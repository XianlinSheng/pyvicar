import numpy as np
import pyvicar.tools.post.dump as dump
import pyvicar.tools.post.dump.labels as lb
import pyvicar.tools.post.dump.plotter_fs as pf
import pyvicar.tools.fp as fp
import pyvicar.tools.log as log


def post_isoq(p):
    c = p.Case(p.name)

    c.dump.read()

    # CASE CHECK: the frames to post
    vtks, markers = c.dump.vtm, c.dump.marker
    # vtks, markers = c.dump.vtm.latest, c.dump.marker.latest
    # vtks, markers = c.dump.vtm[::10], c.dump.marker[::10]

    # CASE CHECK: coloring of q iso surfaces
    iso_color = lb.Color.field(lb.Field.scalar("P"), clim=[-0.5, 0.5], cmap="viridis")
    # iso_color = lb.Color.field(lb.Field.vector("VEL", "z"), clim=[-0.5, 0.5], cmap="viridis")
    # iso_color = lb.Color.field(lb.Field.vector("VEL", "mag"), clim=[0, 1.5], cmap="viridis")

    # CASE CHECK: output name, consider the field for coloring
    outname = "q_p"

    isoq_common_kwargs = {
        "vtks": vtks,
        "markers": markers,
        # CASE CHECK: use the dumpped Q or set as None to auto calc
        "q_name": "Q",
        "iso_color": iso_color,
        "marker_color": lb.Color.uniform("white"),
        "iso_opacity": 0.9,
        "marker_opacity": 1.0,
        "iso_texture": lb.Texture.specular(),
        "marker_texture": lb.Texture.specular(),
        "add_axes": False,
        "show_outline": False,
        "show_grid": False,
        "keep_frames": False,
    }

    cam_common_kwargs = {
        "target": p.gm.center,
        "l0": p.d,
        "r": 10,
        "downstream_shift": 2,
    }

    oclocks = [1, 3, 5, 6, 7, 9, 11, 12]

    for oclock in oclocks:
        log.log_host(f"Post ISOQ: Angle {oclock} o clock")
        c.create_isoq_video(
            plotter_f=pf.set_cam_compass(
                pitch=30,
                oclock=oclock,
                **cam_common_kwargs,
            ),
            out_name=f"{outname}_o{oclock}",
            **isoq_common_kwargs,
        )

    log.log_host(f"Post ISOQ: Top")
    c.create_isoq_video(
        plotter_f=pf.set_cam_compass(
            pitch=90,
            oclock=3,
            **cam_common_kwargs,
        ),
        out_name=f"{outname}_top",
        **isoq_common_kwargs,
    )

    # below plots far view and a mirror/copy of the surface with pressure contour distribution

    mirror_center = p.gm.center + np.array([0, p.d, 0])

    def mirror_f(plotter, c, i, v, m):
        body = m.to_pyvista_multiblocks()[0]
        # choose to mirror or simply copy and translate
        mirrored = body.reflect((0, 1, 0), point=mirror_center)
        # mirrored = body.translate([0, 2 * p.d, 0])
        psurf = lb.Field.rename_scalar("P_SURF", "P")
        plotter.add_mesh(
            dump.prep_field(mirrored, psurf),
            **lb.Color.field(psurf, clim=[-0.5, 0.5]).add_mesh_kwargs(),
            **lb.Texture.specular().add_mesh_kwargs(),
        )
        return plotter

    cam_common_kwargs = {
        "target": mirror_center,
        "l0": p.d,
        "r": 20,
        "downstream_shift": 5,
    }

    for oclock in oclocks:
        log.log_host(f"Post ISOQ: Far & Surf Angle {oclock} o clock")
        c.create_isoq_video(
            plotter_f=fp.pipeline_f(
                mirror_f,
                pf.set_cam_compass(
                    pitch=30,
                    oclock=oclock,
                    **cam_common_kwargs,
                ),
            ),
            out_name=f"{outname}_far_surf_o{oclock}",
            **isoq_common_kwargs,
        )

    log.log_host(f"Post ISOQ: Far & Surf Angle Top")
    c.create_isoq_video(
        plotter_f=fp.pipeline_f(
            mirror_f,
            pf.set_cam_compass(
                pitch=90,
                oclock=3,
                **cam_common_kwargs,
            ),
        ),
        out_name=f"{outname}_far_surf_top",
        **isoq_common_kwargs,
    )
