import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi
from .preprocesses.data import get_vtks_markers
from pyvicar.tools.post.time import slice_by_t


# quick generate
def create_recorder_video(
    c,
    ts,
    vs,
    fig_f,
    vtks,
    dt=None,
    markers=None,
    t1=None,
    t_f=None,
    keep_frames=True,
    out_name="value",
):
    if dt is None and t_f is None:
        raise Exception(f"Either dt or t_f needs to be specified")

    if t_f is None:

        def t_f(tstep):
            return tstep * dt

    c.post.enable()
    c.post.animations.enable()
    a = c.post.animations.get_or_create(out_name)
    a.frames.enable()

    c, vtks, markers = get_vtks_markers(c, vtks, markers)

    mpi.set_async()

    for i, (vtk, marker) in mpi.dispatch(enumerate(zip(vtks, markers))):
        t = t_f(vtk.tstep)
        log.log(f"Recorder Video: Posting frame at tstep = {vtk.tstep}, time = {t}")
        s = slice_by_t(ts, t1, t)

        fig = fig_f(ts[s], *(v[s] for v in vs))

        a.frames.frame_by_matplotlib(i, fig)

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
