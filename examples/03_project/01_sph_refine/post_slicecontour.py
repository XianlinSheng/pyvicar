from pyvicar.case.common import Case
import pyvicar.tools.mpi as mpi
from pyvicar.tools.post.dump import Color, Field


def post_slicecontour(p, run_type="run_check", field="vel"):
    c = Case(p.name)
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
            vtks, markers = c.dump.vtr, c.dump.marker
            keep_frames = False
        case "partial":
            # vtks, markers = c.dump.vtr[-100:], c.dump.marker[-100:]
            vtks, markers = c.dump.vtr[::10], c.dump.marker[::10]
            keep_frames = False
        case _:
            raise Exception(f"Unrecognized run type {run_type}")

    match field:
        case "vel":
            color = Color.field(Field.vector("VEL", "mag"), clim=[0, 1.5])
            outname = "vel"
        case "p":
            color = Color.field(Field.scalar("P"), clim=[-0.5, 0.5])
            outname = "p"
        case "vor":
            color = Color.field(Field.vor_from_vel("VEL", "y"), clim=[-1, 1])
            outname = "vor"
        case _:
            raise Exception(f"Unrecognized field {field}")

    normal = "y"
    origin = [None, None, None]

    # iso full domain view,
    # first use the latest vtm frame for quick check and adjust camera angle, keep the only frame
    # can be run during running to check latest progress
    full = c.create_slicecontour_video(
        vtks,
        markers,
        normal=normal,
        origin=origin,
        contour_color=color,
        keep_frames=keep_frames,
        out_name=f"{outname}_full",
    )

    xyz1 = p.gm.center - 1.5 * p.gm.refl[:, 0] * p.gm.l0[:, 0]
    xyz2 = p.gm.center + 1.5 * p.gm.refl[:, 1] * p.gm.l0[:, 1]
    xyz2[0] = p.gm.center[0] + p.gm.doml[0, 1] * p.gm.l0[0, 1]
    clip_box = [xyz1[0], xyz2[0], xyz1[1], xyz2[1], xyz1[2], xyz2[2]]

    clip = c.create_slicecontour_video(
        vtks,
        markers,
        normal=normal,
        origin=origin,
        clip=clip_box,
        contour_color=color,
        keep_frames=keep_frames,
        out_name=f"{outname}_clip",
    )


from run_test import p

# use run_check during running to check status, angle (latest frame)
# use compress_check after compress to check compress, results, angle (latest frame)
# use full after compress to post formal full video
# use partial after compress to post formal partial, speeded video

# post_slicecontour(p, run_type="run_check", field="vel")
post_slicecontour(p, run_type="compress_check", field="vel")
# post_slicecontour(p, run_type="full", field="vel")
# post_slicecontour(p, run_type="partial", field="vel")

mpi.print_elapsed_time()
