from pyvicar.case.common import Case
import pyvicar.tools.log as log
import pyvicar.tools.mpi as mpi


def compress(p):
    log.log_host(f"Compress Case: {p.name}")
    c = Case(p.name)
    c.dump.vtm.read()
    # default keep_vtm=True in case of mistakes
    c.dump.vtm.to_vtrs(npx=p.npx, npy=p.npy, keep_vtms=True)


# CASE CHECK: the params struct to use
from run import p40

# CASE CHECK: the params struct to use
p = p40

compress(p)

mpi.print_elapsed_time()

# recommend:
# 1. compress but keep vtm
# 2. post
# 3. check both vtr compress and results
# 4. if vtr correct: ./rmvtm.sh name
