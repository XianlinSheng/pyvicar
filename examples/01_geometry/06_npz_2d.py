import pyvicar
from pyvicar.geometry.presets import create_cyl_2d

# 6. npz
# this script generate the case file for a flow past 2D cylinder from npz coord array at Re=200

pyvicar.assert_api_version("1.0.1", "1.1.0")

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

d = 1
U = 1
re = 200
# note: 2D clean dz
dx = d / 50
T = d / U
Umax = 2 * U

# this creates a 2D cylinder npz file at origin, in real uses one should already have the file somewhere
# in npz it has a 2darray xy, shape [npoint, 2], [[x1, y1], ..., [xn, yn]]
# the cylinder is the closed curve point1-p2-p3-...-pn-p1
# to create from your own np array, using: np.savez(filename, xy=xy_coord_array)
create_cyl_2d(d / 2, dx, [0, 0], file="tut_npz_cyl.npz")

c = Case("tut_npz")

# note: 2D mesh parameters
gm = c.create_grid(
    l0=d,
    dx=dx,
    dim2=True,
    doml=[[10, 8], 10],
    refl=1.5,
    grow=[[1.05, 1.02], 1.03],
)

# this read the npz and emplace at gm.center
body, surf = c.append_npz_solid_2d("tut_npz_cyl.npz", gm.center)

c.set_inlet("x1", [U, 0, 0])

c.set_re(re, U=U, L=d)

# note: 2D poisson tol
c.set_tstep(U=Umax, dx=dx, T=T, nT=10, nsteps_unit=10, ndumps=10, step_test=False, divu_tol=1e-4)

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
