import pyvicar
from pyvicar.geometry.presets import create_plane_2d
import numpy as np

# 9. npz memb
# this script generate the case file for a flow past 2D plane membrane from npz coord array at Re=200

pyvicar.assert_api_version("1.0.2", "1.1.0")  # append_npz_membrane_2d is added in 1.0.2

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

d = 1
U = 1
re = 200
dx = d / 20
T = d / U
Umax = 2 * U
alpha = 5
alpha_rad = np.radians(alpha)

# this creates a 2D plane (2d straight line) npz file at origin,
# in real uses one should already have the file somewhere
vec = d * np.array([np.cos(alpha_rad), -np.sin(alpha_rad)])
create_plane_2d(vec, dx, [0, 0], file="tut_npz_plane.npz")

c = Case("tut_npz_memb")

gm = c.create_grid(l0=d, dx=dx, dim2=True, refl=[[3, None], 3])
#                                          ^~~~~~~~~~~~~~~~~~~ remember stricter 2d refine requirement
#                                                              no longer needed starting from d/50
#                                                              typical decent sim. needs at least d/100
#                               ^~~~~~ remember this when creating 2D grid,
#                                      but you can always check for possible mistakes by show_grid()

body, surf, om2e = c.append_npz_membrane_2d("tut_npz_plane.npz", gm.center)
#         ^~~~~~ remember this when creating 2d membrane
# specify cycled=False (default) when the curve is not closed, no segments between [xn, yn] and [x0, y0]
# this is an open membrane and will append a new c.om2edge.om2s[inew] item and also return here
# specify cycled=True if it is closed, and for a closed membrane no new om2edge item will be created
# the 3rd return object here will be None

c.set_inlet("x1", [U, 0, 0])

c.set_re(re, U=U, L=d)

c.set_tstep(U=Umax, dx=dx, T=T, nT=10, nsteps_unit=10, ndumps=10, step_test=False)

c.set_partition(nproc_node=16, nnode_max=1)

c.job.enable()
c.job.account = "account"
c.job.partition = "partition"

c.job.condaDeactivate = True
c.job.modulePurge = True
c.job.moduleUse = True
c.job.moduleLoad = True
c.job.logfile = ""
c.job.output = "log.out"
c.job.error = "log.err"

c.write()

# c.show_grid(gm.center)

c.stat_grid()
c.stat_tstep(
    cfl={"U": Umax, "dx": dx},
    tdt={"T": T},
    ndmp={"T": T},
)
c.stat_viscosity(
    re={"U": U, "L": d},
    yplus={"y": dx, "tau": {"U": U, "L": d}},
)
c.stat_partition()

# c.bash()
# c.sbatch()
