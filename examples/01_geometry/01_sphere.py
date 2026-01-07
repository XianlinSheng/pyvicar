from pyvicar.case.common import Case

# 1. sphere
# this script generate the case file for a flow past sphere at Re=200, run for one time step

d = 1
U = 1
re = 200
dx = d / 20

# this defines a case directory ./tut_sphere,
# one can also manually create folders and place this .py inside with Case(".")
c = Case("tut_sphere")

# return a GridModel, containing domain, refinement buffer sizes, and growth rates, check by print(gm)
gm = c.create_grid(l0=d, dx=dx)
#                        ^ finest grid spacing, forced dx=dy=dz in refinement region in create_grid method
#                  ^ length scale, default refine region will be relative to this scale

# body is body motion/dynamics/... settings, surf is triangular geometry settings
# "append" means append to body list
body, surf = c.append_sphere(d / 2, dx, gm.center)

# note that body is defined after grid because the solver domain always starts at 0,0,0
# and the position to place the body depends on how we define the domain and refine the grid

c.set_inlet("x1", [U, 0, 0])
c.set_re(re, U=U, L=d)  # U and L are needed since solver uses 1/nu

# enable and set SRJ solver params (needed in pbicgstab)
# one can use other configs like set_params("P3N128"), which will first generate a database if not exist
c.srj.enable()
c.srj.set_params()

# show grid preview and statistics, use c.stat_grid() to print statistics alone
c.show_grid(gm.center)

# c.job.enable()
# c.job.jobName = "tut_sphere"
# c.job.account = "account"

# write the case input files
c.write()


# uncomment the c.mpirun() to start run locally
# both need the ~/Vicar3D/versions/common/src/Vicar3D executable

# c.mpirun()

# c.sbatch()
