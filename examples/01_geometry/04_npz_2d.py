from pyvicar.case.common import Case
from pyvicar.geometry.presets import create_cyl_2d

# 4. npz
# this script generate the case file for a flow past 2D cylinder from npz coord array at Re=200, run for one time step

d = 1
U = 1
re = 200
dx = d / 20

# this creates a 2D cylinder npz file at origin, in real uses one should already have the file somewhere
# in npz it has a 2darray xy, shape [npoint, 2], [[x1, y1], ..., [xn, yn]]
# the cylinder is the closed curve point1-p2-p3-...-pn-p1
# to create from your own np array, using: np.savez(filename, xy=xy_coord_array)
create_cyl_2d(d / 2, dx, [0, 0], file="tut_npz_cyl.npz")

c = Case("tut_npz")

gm = c.create_grid(l0=d, dx=dx, dim2=True)
#                               ^~~~~~ remember this when creating 2D grid,
#                                      but you can always check for possible mistakes by show_grid()

# this read the npz and emplace at gm.center
body, surf = c.append_npz_solid_2d("tut_npz_cyl.npz", gm.center)

# below is completely the same as example 1/2/3

c.set_inlet("x1", [U, 0, 0])
c.set_re(re, U=U, L=d)

c.srj.enable()
c.srj.set_params()

c.show_grid(gm.center)

c.write()


# c.mpirun()

# c.job.enable()
# c.job.jobName = "tut_npz"
# c.job.account = "account"
# c.sbatch()
