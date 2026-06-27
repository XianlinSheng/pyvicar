import sys
import projmgr as mgr
import pyvicar.tools.mpi as mpi
import pyvicar.tools.log as log

# usage  : python post.py <job> <code> ...
# example: python post.py compress re1000devr120LC

job = sys.argv[1]
codes = sys.argv[2:]
# code = ["re1000devr120LC"]

pf = mgr.postlib.import_func(job)

if pf.mpi_async:
    codes = mpi.dispatch(codes)
    log.log_host(f"Job {job} supports MPI Async parallel")
    mpi.set_async()
else:
    log.log_host(
        f"Job {job} does not support MPI Async parallel, cases will be processed sequentially"
    )


for code in codes:
    if pf.mpi_async:
        log.log(f"Post {job} {code}")
    else:
        log.log_host(f"Post {job} {code}")

    p = mgr.studies.to_params(code)

    pf.f(p)

mpi.print_elapsed_time()
