from .jobs import FullStatus, Status, JobOutputError, Loop
import pyvicar.tools.mpi as mpi
import pyvicar.tools.log as log
from pyvicar._format.tools import Table
import numpy as np
from mpi4py import MPI


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
    st.g.loop["jobs_frameproc_time"] = np.zeros(len(jobs))

    while st.g.loop["continue"]:
        for job in jobs:
            job.frame_begin(st)

        for ijob, job in enumerate(jobs):
            t0 = MPI.Wtime()
            job.frame_proc(st)
            dt = MPI.Wtime() - t0
            st.g.loop["jobs_frameproc_time"][ijob] += dt

        for job in jobs:
            job.frame_end(st)

    for job in jobs:
        job.global_end(st)

    log.log_host(f"Post: frame process avg time")
    table = Table.create()
    table.add(["No.", "Job Name", "Avg Frame Proc (s)", "% Total"])
    times = st.g.loop["jobs_frameproc_time"]
    tot_time = np.sum(times)
    for ijob, (job, time) in enumerate(zip(jobs, times)):
        table.add([f"{ijob}", job.name(), f"{time:.2f}", f"{time/tot_time*100:6.2f}%"])
    table.add(["", "Total", f"{tot_time:.2f}"])
    table.format().log_host()

    return st
