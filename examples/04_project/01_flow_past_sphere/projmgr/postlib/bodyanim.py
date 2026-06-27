import pyvicar
import pyvicar.tools.post.dump.labels as lb
import pyvicar.tools.post.dump.plotter_fs as pf
import pyvicar.tools.log as log

pyvicar.assert_api_version("1.0.2", "1.1.0")

mpi_async = False


def post_bodyanim(p):
    c = p.Case(p.name)

    c.dump.read()

    # CASE CHECK: the frames to post
    markers = c.dump.marker
    # markers = c.dump.marker.latest
    # markers = c.dump.marker[::10]

    # CASE CHECK: output name, consider the field for coloring
    outname = "body"

    bodyanim_common_kwargs = {
        "markers": markers,
        # CASE CHECK: use the dumpped Q or set as None to auto calc
        "marker_color": lb.Color.uniform("gray"),
        "marker_opacity": 1.0,
        "marker_texture": lb.Texture.specular(),
        "add_axes": False,
        "show_grid": False,
        "keep_frames": False,
    }

    cam_common_kwargs = {
        "target": p.gm.center,
        "l0": p.d,
        "r": 6,
        "downstream_shift": 0,
    }

    oclocks = [1, 3, 5, 6, 7, 9, 11, 12]

    for oclock in oclocks:
        log.log_host(f"Post Body Anim: Angle {oclock} o clock")
        c.create_bodyanim_video(
            plotter_f=pf.set_cam_compass(
                pitch=30,
                oclock=oclock,
                **cam_common_kwargs,
            ),
            out_name=f"{outname}_o{oclock}",
            **bodyanim_common_kwargs,
        )

    log.log_host(f"Post Body Anim: Top")
    c.create_bodyanim_video(
        plotter_f=pf.set_cam_compass(
            pitch=90,
            oclock=3,
            **cam_common_kwargs,
        ),
        out_name=f"{outname}_top",
        **bodyanim_common_kwargs,
    )
