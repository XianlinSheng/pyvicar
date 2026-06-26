import sys
import projmgr as mgr
import pyvicar.tools.mpi as mpi
import pyvicar.tools.log as log

# usage  : python stat.py <job> ...
# example: python stat.py rs_dlcurve sg_dlbar

jobs = sys.argv[1:]

par_sfs = []
seq_sfs = []
for job in jobs:
    sf = mgr.statlib.import_func(job)
    if sf.mpi_async:
        par_sfs.append(sf)
        log.log_host(f"Job {job} supports MPI Async parallel")
    else:
        seq_sfs.append(sf)
        log.log_host(
            f"Job {job} does not support MPI Async parallel, will be processed sequentially"
        )


mpi.set_async()
for sf in mpi.dispatch(par_sfs):
    log.log(f"Stat {sf.name}")
    sf.f()


mpi.set_sync()
log.log_host(f"Parallel jobs done, start sequential jobs")
for sf in seq_sfs:
    log.log_host(f"Stat {sf.name}")
    sf.f()

mpi.print_elapsed_time()
