import pyvicar
import numpy as np

# 3. plane
# this script generates the case file for a flow past planar membrane at Re=200

pyvicar.assert_api_version("1.0.1", "1.1.0")

# change this to the install position
Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

d = 1
U = 1
re = 200
dx = d / 20
T = d / U
Umax = 2 * U
alpha = 5  # angle of attack
alpha_rad = np.radians(alpha)

c = Case("tut_plane")

gm = c.create_grid(l0=d, dx=dx)

# append_plane(uxyz, vxyz, dx, xyz0=None)
# defined by an origin xyz0, and uv vectors uxyz, vxyz (magnitude is the edge length)
# 4 vertices are xyz0, xyz0 + uxyz, xyz0 + vxyz, xyz0 + uxyz + vxyz, xyz0=None for [0, 0, 0]
# generated trisurf normal is cross(u, v) direction
uxyz = np.array([0, -d, 0])
vxyz = np.array([d * np.cos(alpha_rad), 0, -d * np.sin(alpha_rad)])
cxyz = (uxyz + vxyz) / 2  # center
body, surf = c.append_plane(uxyz, vxyz, dx, gm.center - cxyz)
# note gm.center - [a, b, c] is valid since gm.center is np.array and it can operate with pylist

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
