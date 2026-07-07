import pyvicar
from pyvicar.grid import GridModel
import numpy as np

# 3. plane heave pitch
# this script generates the case file for a flow past sine-oscillating heaving and pitching plane
# Re=U*L/nu=200, St=2*A*f/U=0.2, T=5, A is amp so 2*A is peak-to-peak length, aoa -30 to 30deg, 30 upstroke
# effective flow pitch at max vel = atan(2*pi*f*A/U) = atan(pi*St)
# effective aoa = eff. flow pitch - aoa amp

pyvicar.assert_api_version("1.0.1", "1.1.0")

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
dx = d / 20

c = Case("tut_plane_heavepitch")

gm = GridModel.create(
    l0=d,
    doml=[[20, 5], 20, 20],
    refl=[[1, 2.5], 1, 1],
    grow=[[1.4, 1.02], 1.4, 1.4],
)

gm.refl[2, :] += A / d

c.apply_grid_model(gm, dx=dx)

uxyz = np.array([0, -d, 0])
vxyz = d * np.array([1, 0, 0])
cxyz = (uxyz + vxyz) / 2
xyz0 = gm.center - cxyz - [0, 0, A]
body, surf = c.append_plane(uxyz, vxyz, dx, xyz0)
body.general.motionType = "forced"
body.motion.ampz = vamp
body.motion.freqz = f
body.motion.phase = 90  # starts at the beginning of upstroke, vang at +amp decreasing
body.motion.ampangy = alpha_vamp
body.motion.freqangy = f
# rotation center at initial tstep, will move with translation
body.position.centx = xyz0[0]
body.position.centy = xyz0[1]
body.position.centz = xyz0[2]

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
