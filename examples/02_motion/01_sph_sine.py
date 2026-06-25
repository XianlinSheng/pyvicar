import pyvicar
from pyvicar.grid import GridModel
import numpy as np

# 1. sph sine
# this script generates the case file for a flow past sine-oscillating sphere
# Re=U*L/nu=200, St=2*A*f/U=0.3, A is amp so 2*A is peak-to-peak length
# effective flow pitch at max vel = atan(2*pi*f*A/U) = atan(pi*St)

pyvicar.assert_api_version("1.0.1", "1.1.0")

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

d = 1
U = 1
re = 200
st = 0.3
A = d / 2
f = st * U / A / 2
T = 1 / f
vamp = 2 * np.pi * f * A
Umax = np.sqrt((2 * U) ** 2 + vamp**2)
dx = d / 20

c = Case("tut_sph_sine")

# manually create a grid structure to cover the moving region
# l0 doml refl grow are structured in [[x-, x+], [y-, y+], [z-, z+]],
# for 2d grid, specify dim2=True and only [[x-, x+], [y-, y+]]
# one can replace a list by a single var, which means to broadcast:
# [x, [y-, y+], [z-, z+]] == [[x, x], ...]
# a == [a, a, a] == [[a, a], [a, a], [a, a]]
# doml/refl mean the domain/refine box length (normalized by l0) in corresponding direction
# grow is the growth rate in corresponding direction
# var can be None, which means to use the default values
# below are the defaults of doml refl grow, l0 default is all 1
gm = GridModel.create(
    l0=d,
    doml=[[20, 5], 20, 20],
    refl=[[1, 2.5], 1, 1],
    grow=[[1.4, 1.02], 1.4, 1.4],
)
# expand the refine box for moving body
# these are all in numpy arrays, [axis (xyz), side (-+)]
# so this below is increasing z- z+ by A
gm.refl[2, :] += A / d

# apply a grid design at a specified spacing and create the grid
# the gm = create_grid(l0=..., dx=..., doml=..., ...) in 01_geometry examples
# is under the hood creating a GridModel with l0 doml ... and apply at dx and return it
c.apply_grid_model(gm, dx=dx)

# forced motion is w = ampz*sin(2*pi*freqz*t), so starting point is zmin
body, surf = c.append_sphere(d / 2, dx, gm.center - [0, 0, A])
# there is a body.motion.phase var but its only for angular velocities
body.general.motionType = "forced"
body.motion.ampz = vamp
body.motion.freqz = f

c.set_inlet("x1", [U, 0, 0])

c.set_re(re, U=U, L=d)  # U and L are needed since solver uses 1/nu

# for periodic case a cycle typically must contain n*100 steps,
# on fine mesh like >=d/80 one can set 2000
# (optional, only to make a good tstep number like 2000-4000-6000 rather than 1700-3400-5100)
c.set_tstep(U=Umax, dx=dx, T=T, nT=3, nsteps_unit=100, ndumps=50, step_test=False)

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
