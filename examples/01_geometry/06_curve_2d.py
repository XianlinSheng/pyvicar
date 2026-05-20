import numpy as np
import pyvicar
from pyvicar.geometry.presets import create_cyl_2d

# 6. curve 2D
# this script generate the case file for a flow past 2D cylinder at Re=200,
# where the cylinder is described by a np array, xy coords for points.
# in shape [npoint, 2], [[x1, y1], ..., [xn, yn]], same format as the npz xy array in example 4

pyvicar.assert_api_version("1.0.1", "1.1.0")

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

d = 1
U = 1
re = 200
dx = d / 20
T = d / U
Umax = 2 * U

# this preset gives a np array for xy coord of all points
curv = create_cyl_2d(d / 2, dx, [0, 0])

# this create_cyl_2d(...) is exactly the same function in example 4,
# it always returns the xy coord np array in runtime memory,
# but does not write it to npz file if file=... is not specified

c = Case("tut_curve_2d")

gm = c.create_grid(l0=d, dx=dx, dim2=True, refl=[[3, None], 3])
#                                          ^~~~~~~~~~~~~~~~~~~ remember stricter 2d refine requirement
#                                                              no longer needed starting from d/50
#                                                              typical decent sim. needs at least d/100
#                               ^~~~~~~~~ dont forget this in 2D case

# this emplaces a translated 2D closed curve,
# gm.center auto returns len-2 xy coord in 2D, np.newaxis is to broadcast to all points
body, surf = c.append_solid_2d(curv + gm.center[np.newaxis, :])

c.set_inlet("x1", [U, 0, 0])

c.set_re(re, U=U, L=d)

c.set_tstep(U=Umax, dx=dx, T=T, nT=10, nsteps_unit=10, ndumps=10, step_test=False)

c.set_partition(nproc_node=16, nnode_max=1)

c.job.enable()
c.job.account = "account"
c.job.partition = "partition"

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
