import numpy as np
from pyvicar.case.common import Case
from pyvicar.geometry.presets import create_cyl_2d

# 6. curve 2D
# this script generate the case file for a flow past 2D cylinder at Re=200, run for one time step,
# where the cylinder is described by a np array, xy coords for points.
# in shape [npoint, 2], [[x1, y1], ..., [xn, yn]], same format as the npz xy array in example 4

d = 1
U = 1
re = 200
dx = d / 20

# this preset gives a np array for xy coord of all points
curv = create_cyl_2d(d / 2, dx, [0, 0])

# this create_cyl_2d(...) is exactly the same function in example 4,
# it always returns the xy coord np array in runtime memory,
# but does not write it to npz file if file=... is not specified

c = Case("tut_curve_2d")

gm = c.create_grid(l0=d, dx=dx, dim2=True)
#                               ^~~~~~~~~ dont forget this in 2D case

# this emplaces a translated 2D closed curve,
# gm.center auto returns len-2 xy coord in 2D, np.newaxis is to broadcast to all points
body, surf = c.append_solid_2d(curv + gm.center[np.newaxis, :])


# below is completely the same as example 1/2/3/4/5

c.set_inlet("x1", [U, 0, 0])
c.set_re(re, U=U, L=d)

c.srj.enable()
c.srj.set_params()

c.show_grid(gm.center)

c.write()


# c.mpirun()

# c.job.enable()
# c.job.jobName = "tut_curve_2d"
# c.job.account = "account"
# c.sbatch()
