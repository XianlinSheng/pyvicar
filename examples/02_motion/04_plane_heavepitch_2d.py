import pyvicar
from pyvicar.grid import GridModel
import numpy as np

# 4. plane heave pitch 2d
# this script generates the case file for a flow past sine-oscillating heaving and pitching 2d plane
# Re=U*L/nu=200, St=2*A*f/U=0.2, T=5, A is amp so 2*A is peak-to-peak length, aoa -30 to 30deg, 30 upstroke
# effective flow pitch at max vel = atan(2*pi*f*A/U) = atan(pi*St)
# effective aoa = eff. flow pitch - aoa amp

pyvicar.assert_api_version("1.0.2", "1.1.0")

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

d = 1
U = 1
re = 200
st = 0.2
A = d / 2
f = st * U / A / 2
T = 1 / f
vamp = 2 * np.pi * f * A
alpha_amp = 30
alpha_amp_rad = np.radians(alpha_amp)
alpha_vamp = 2 * np.pi * f * alpha_amp_rad
Umax = np.sqrt((2 * U) ** 2 + vamp**2)
# note: 2D clean dz
dx = d / 50

c = Case("tut_plane_heavepitch_2d")

# note: 2D mesh parameters
gm = GridModel.create(
    l0=d,
    doml=[[10, 8], 10],
    refl=1.5,
    grow=[[1.05, 1.02], 1.03],
    dim2=True,
)
# note: 2d up-down is y direction
gm.refl[1, :] += A / d

c.apply_grid_model(gm, dx=dx)

vec0 = d * np.array([1, 0])
xy0 = gm.center - vec0 / 2 - [0, A]
body, surf, om2e = c.append_plane_2d(vec0, dx, xy0)
body.general.motionType = "forced"
body.motion.ampy = vamp
body.motion.freqy = f
body.motion.phase = -90  # starts at the beginning of upstroke, vang at -amp increasing
body.motion.ampangz = alpha_vamp
body.motion.freqangz = f
# rotation center at initial tstep, will move with translation
body.position.centx = xy0[0]
body.position.centy = xy0[1]

c.set_inlet("x1", [U, 0, 0])

c.set_re(re, U=U, L=d)  # U and L are needed since solver uses 1/nu

# note: 2D poisson tol
c.set_tstep(
    U=Umax, dx=dx, T=T, nT=3, nsteps_unit=100, ndumps=50, step_test=False, divu_tol=1e-4
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
