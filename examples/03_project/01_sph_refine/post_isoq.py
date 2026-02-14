import pyvicar as pvc
import pyvicar.tools.mpi as mpi
import pyvicar.tools.log as log
from pyvicar.tools.post.dump import Color, Field, set_cam_compass


def post_isoq(p, run_type="run_check"):
    c = p.Case(p.name)
    c.dump.read()

    # None, None is default run check, using the latest vtm
    match run_type:
        case "run_check":
            vtks, markers = None, None
            keep_frames = True
        case "compress_check":
            vtks, markers = c.dump.vtr.latest, c.dump.marker.latest
            keep_frames = True
        case "full":
            # CASE CHECK: vtr or vtm?
            vtks, markers = c.dump.vtr, c.dump.marker
            keep_frames = False
        case "partial":
            # CASE CHECK: vtr or vtm?
            # vtks, markers = c.dump.vtr[-100:], c.dump.marker[-100:]
            vtks, markers = c.dump.vtr[::10], c.dump.marker[::10]
            keep_frames = False
        case _:
            raise Exception(f"Unrecognized run type {run_type}")

    color = Color.field(Field.vector("VEL", "z"), clim=[-0.5, 0.5])
    # color=Color.field(Field.vector("VEL", "mag"), clim=[0, 1.5]),
    # color=Color.field(Field.scalar("P"), clim=[-0.5, 0.5]),

    outname = "q_w"

    # iso full domain view,
    # first use the latest vtm frame for quick check and adjust camera angle, keep the only frame
    # can be run during running to check latest progress
    log.log_host(f"Post ISOQ: ISO Angle")
    iso = c.create_isoq_video(
        vtks,
        markers,
        iso_color=color,
        keep_frames=keep_frames,
        out_name=f"{outname}_iso",
    )

    # assume already compressed, using c.dump.vtr
    log.log_host(f"Post ISOQ: Angle 1")
    a2 = c.create_isoq_video(
        vtks,
        markers,
        # CASE CHECK: length scale
        plotter_f=set_cam_compass(p.gm.center, l0=p.d),
        # plotter_f=set_cam_compass(
        #     p.gm.center, l0=p.d, r=4, oclock=2, pitch=30, downstream_shift=1
        # ),
        iso_color=color,
        keep_frames=keep_frames,
        out_name=f"{outname}_o2",
    )

    # or change a view angle if you want
    log.log_host(f"Post ISOQ: Angle 2")
    a10 = c.create_isoq_video(
        vtks,
        markers,
        # CASE CHECK: length scale
        plotter_f=set_cam_compass(p.gm.center, l0=p.d, oclock=10),
        iso_color=color,
        keep_frames=keep_frames,
        out_name=f"{outname}_o10",
    )


# CASE CHECK: the params struct to use
from run import p40

# CASE CHECK: the params struct to use
p = p40

# use run_check during running to check status, angle (latest frame)
# use compress_check after compress to check compress, results, angle (latest frame)
# use full after compress to post formal full video
# use partial after compress to post formal partial, speeded video

# CASE CHECK: select run type: run_check, compress_check, full, partial
post_isoq(p, run_type="compress_check")

mpi.print_elapsed_time()
