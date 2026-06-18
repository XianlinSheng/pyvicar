import numpy as np
import pyvicar
from pyvicar.geometry.presets import create_cyl_2d, create_plane_2d

# 12. curve 2D
# this script generate the case file for a flow past 2D cylinder and 2D plane membrane at Re=200,
# where both point series are described by a np array, xy coords for points.
# in shape [npoint, 2], [[x1, y1], ..., [xn, yn]], same format as the npz xy array in example 6

pyvicar.assert_api_version("1.0.1", "1.1.0")

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

d = 1
U = 1
re = 200
dx = d / 20
T = d / U
Umax = 2 * U
alpha = 5
alpha_rad = np.radians(alpha)

# same as mentioned in example 11, these two are the same functions in example 6/9
# unlike 3D that needs TriSurface to represent a triangular surface,
# 2D only needs a xy point list, so the returned value here is simply a numpy array
# its shaped in [npoint, 2], so [i, :] is [xi, yi]
curv_solid = create_cyl_2d(d / 2, dx, [0, 0])

vec = d * np.array([np.cos(alpha_rad), -np.sin(alpha_rad)])
curv_memb = create_plane_2d(vec, dx, [0, 0])

c = Case("tut_curve_2d")

gm = c.create_grid(l0=d, dx=dx, dim2=True, refl=[[4, 3.5], 3], doml=[[None, 6], None])
#                                          ^~~~~~~~~~~~~~~~~~~ remember stricter 2d refine requirement
#                                                              no longer needed starting from d/50
#                                                              typical decent sim. needs at least d/100
#                               ^~~~~~~~~ dont forget this in 2D case

# this emplaces a translated 2D closed curve,
# gm.center auto returns len-2 xy coord in 2D, np.newaxis is to broadcast to all points
body, surf = c.append_solid_2d(
    curv_solid + gm.center[np.newaxis, :] - np.array([d, 0])[np.newaxis, :]
)
# body.general.motionType = "forced"
# body.motion.ampy = 0.01
# body.motion.freqy = 0.1

body, surf, om2e = c.append_membrane_2d(
    curv_memb + gm.center[np.newaxis, :] + np.array([d, 0])[np.newaxis, :]
)
#         ^~~~~~ remember to take the additional om2e (open membrane edge) for 2d membrane
#                even if one may set up a closed one, placehoder still needed for the returned None

# surf.to_trisurf().show()

# note that solid is a closed curve, the segments are point1-p2, p2-p3, ..., pn-p1
# membrane can be either open or closed, default open, or specify closed=True its closed
# in either case, if the curve is closed, NO need to add a repeated x1 at the end of the list

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
