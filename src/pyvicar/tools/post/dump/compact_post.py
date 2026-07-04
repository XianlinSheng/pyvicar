from .jobs import FullStatus, Status, JobOutputError, Loop
import pyvicar.tools.mpi as mpi


# need at least one read job on either vtk/marker, or otherwise theres nothing to do
def compact_post(job_read, *jobs):
    st = FullStatus(Status(), Status())

    job_read.global_begin(st)

    outputs = st.g[job_read.name()]

    try:
        nframes = outputs["nframes"]
    except KeyError:
        raise JobOutputError(
            f"Expected the first job to be a read job, and a read job should set a 'nframes' variable as the number of frames in its global outputs st.g[name]"
        )

    # an implicit Loop control job, in principle job list should be [loop, read0, *jobs],
    # but since loop can be derived from read0, it is created internally
    job_loop = Loop(nframes)

    job_loop.global_begin(st)

    for job in jobs:
        job.global_begin(st)

    # from this point, all jobs can be treated in the same way
    jobs = [job_loop, job_read, *jobs]

    while st.g.loop["continue"]:
        for job in jobs:
            job.frame_begin(st)

        for job in jobs:
            job.frame_proc(st)

        for job in jobs:
            job.frame_end(st)

    for job in jobs:
        job.global_end(st)

    return st
