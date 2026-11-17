import sys
import os
import projmgr as mgr
import pyvicar.tools.mpi as mpi
import pyvicar.tools.log as log
from glob import glob

os.chdir("sims")

# usage  : python post.py <job> <code> ...
# example: python post.py compress re200rec

job = sys.argv[1]
codes = [
    match
    for pattern in sys.argv[2:]
    for match in glob(pattern)
]
if not codes:
    raise FileExistsError(f"Code patterns do not match with anything: {sys.argv[2:]}")

pf = mgr.postlib.import_func(job)

if pf.mpi_async:
    codes = mpi.dispatch(codes)
    log.log_host(f"Job {job} supports MPI Async parallel")
    mpi.set_async()
else:
    log.log_host(
        f"Job {job} does not support MPI Async parallel, cases will be processed sequentially"
    )


failures = []
for code in codes:
    if pf.mpi_async:
        log.log(f"Post {job} {code}")
    else:
        log.log_host(f"Post {job} {code}")

    try:
        p = mgr.studies.to_params(code)
        pf.f(p)
    except Exception as e:
        failures.append(f"Failure {code}: {e}")

mpi.barrier()
log.log_host(f"Finished all runnable jobs")

for failure in failures:
    if pf.mpi_async:
        log.log(failure)
    else:
        log.log_host(failure)


mpi.print_elapsed_time()
