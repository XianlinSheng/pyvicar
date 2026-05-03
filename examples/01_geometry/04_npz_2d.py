import pyvicar
from pyvicar.geometry.presets import create_cyl_2d

# 4. npz
# this script generate the case file for a flow past 2D cylinder from npz coord array at Re=200

pyvicar.assert_api_version("1.0.1", "1.1.0")

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

d = 1
U = 1
re = 200
dx = d / 20
T = d / U
Umax = 2 * U

# this creates a 2D cylinder npz file at origin, in real uses one should already have the file somewhere
# in npz it has a 2darray xy, shape [npoint, 2], [[x1, y1], ..., [xn, yn]]
# the cylinder is the closed curve point1-p2-p3-...-pn-p1
# to create from your own np array, using: np.savez(filename, xy=xy_coord_array)
create_cyl_2d(d / 2, dx, [0, 0], file="tut_npz_cyl.npz")

c = Case("tut_npz")

gm = c.create_grid(l0=d, dx=dx, dim2=True, refl=[[3, None], 3])
#                                          ^~~~~~~~~~~~~~~~~~~ remember stricter 2d refine requirement
#                                                              no longer needed starting from d/50
#                                                              typical decent sim. needs at least d/100
#                               ^~~~~~ remember this when creating 2D grid,
#                                      but you can always check for possible mistakes by show_grid()

# this read the npz and emplace at gm.center
body, surf = c.append_npz_solid_2d("tut_npz_cyl.npz", gm.center)

c.set_inlet("x1", [U, 0, 0])

c.set_re(re, U=U, L=d)

c.set_tstep(U=Umax, dx=dx, T=T, nT=10, nsteps_unit=10, ndumps=10, step_test=False)

c.set_partition(nproc_node=16, nnode_max=1)

c.job.enable()
c.job.account = "account"

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
