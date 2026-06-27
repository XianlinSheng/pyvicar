import pyvicar
from pyvicar.geometry.presets import create_plane
import numpy as np

# 8. stl memb
# this script generate the case file for a flow past stl plane membrane at Re=200

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

# this creates a plane stl file at origin, in real uses one should already have the file somewhere
uxyz = np.array([0, -d, 0])
vxyz = np.array([d * np.cos(alpha_rad), 0, -d * np.sin(alpha_rad)])
create_plane(uxyz, vxyz, dx, [0, 0, 0], file="tut_stl_plane.stl")

c = Case("tut_stl_memb")

gm = c.create_grid(l0=d, dx=dx)

body, surf = c.append_stl_membrane("tut_stl_plane.stl", gm.center)
#                        ^~~~~~~~~ different from example 5 append_stl_solid

# stl is considered only for 3D body in 3D case because 2D body should simply be a point list.
# even though 2D body is stored as an extruded 3D triangular surface in the solver,
# using stl to store its 2D shape yourself introduces redundant info and dynamic dependencies like dz,
# so recommend storing it using npz numpy array or csv in example 6/7, and let pyvicar handle the conversion

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
