from pyvicar.case.common import Case

# 2. cylinder 2d
# this script generate the case file for a flow past 2D cylinder at Re=200, run for one time step

d = 1
U = 1
re = 200
dx = d / 20

c = Case("tut_cyl2d")

gm = c.create_grid(l0=d, dx=dx, dim2=True)
#                               ^~~~~~~~~ different from example 1, this will create a 2D grid
# 2D case is still using a 3d grid, but only 3 nodes (2 segments) in z direction
# note that 2D is still explicit to solver, and it behaves slightly differently from 3D cases

body, surf = c.append_cyl_2d(d / 2, dx, gm.center)
#                     ^~~~~~ different from example 1
# same, 2D body is a 3D surface, extruded along z and aligned with z layer, check in show_grid() output
# to see only the geometry in detail, using surf.to_trisurf().show(),
# to_trisurf() extracts and rearranges needed info in the config and create a TriSurface geometry object

c.set_inlet("x1", [U, 0, 0])
c.set_re(re, U=U, L=d)

c.srj.enable()
c.srj.set_params()

c.show_grid(gm.center)

# c.job.enable()
# c.job.jobName = "tut_cyl2d"
# c.job.account = "account"

c.write()


# c.mpirun()

# c.sbatch()
