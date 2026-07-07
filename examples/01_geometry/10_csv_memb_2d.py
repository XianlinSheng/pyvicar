import pyvicar
from pyvicar.geometry.presets import create_plane_2d
import numpy as np

# 10. csv memb
# this script generate the case file for a flow past 2D plane membrane from csv coord columns at Re=200

pyvicar.assert_api_version("1.0.2", "1.1.0")  # append_csv_membrane_2d is added in 1.0.2

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

d = 1
U = 1
re = 200
# note: 2D clean dz
dx = d / 50
T = d / U
Umax = 2 * U
alpha = 5
alpha_rad = np.radians(alpha)

vec = d * np.array([np.cos(alpha_rad), -np.sin(alpha_rad)])
create_plane_2d(vec, dx, [0, 0], file="tut_csv_plane.csv")

c = Case("tut_csv_memb")

# note: 2D mesh parameters
gm = c.create_grid(
    l0=d,
    dx=dx,
    dim2=True,
    doml=[[10, 8], 10],
    refl=1.5,
    grow=[[1.05, 1.02], 1.03],
)

body, surf, om2e = c.append_csv_membrane_2d("tut_csv_plane.csv", gm.center)
#         ^~~~~~ remember this when creating 2d membrane

c.set_inlet("x1", [U, 0, 0])

c.set_re(re, U=U, L=d)

# note: 2D poisson tol
c.set_tstep(
    U=Umax, dx=dx, T=T, nT=10, nsteps_unit=10, ndumps=10, step_test=False, divu_tol=1e-4
)

c.set_partition(nproc_node=16, nnode_max=1)

# note: 2D upwind
c.input.hybridization.upwindWeight = 0.1

# note: 2D poisson iter
c.input.poisson.itermaxPoisson = 3000

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
