import pyvicar

# 1. sphere
# this script generates the case file for a flow past sphere at Re=200

# if using certain features in the script, assert pyvicar version first
# generally version a.b.x is backward supported for all x
# attempts of feature change or deletion will be gathered till the next a.b+1.0
# this assert is introduced starting from 1.0.1
pyvicar.assert_api_version("1.0.1", "1.1.0")

# change this to the install position
Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

d = 1
U = 1
re = 200
dx = d / 20
T = d / U
Umax = 2 * U

# this defines a case directory ./tut_sphere,
# one can also manually create folders and place this .py inside with Case(".")
c = Case("tut_sphere")

# one can simply set every single entry manually like
# c.input.parallel.npx = npx, c.xgrid...., c.canonicalBody....
# but it is complex, coupled, prone to errors, and difficult to make a minimal starting test example,
# so it is recommended to use the following pyvicar tools. inside each tool function,
# pyvicar api simply first auto calculates and then does the same c.xxx.yyy.... settings

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

# U and dx are used to calculate cfl constraints
# T is a time scale to base on, can be the period in oscillations or a characteristic time like here
# nT is how many T times to run
# other default values are
# cfl_max=0.4, nsteps_unit=2000, nrestart_max=100, ndumps=50, divu_tol=1e-6, step_test=False
# set step_test=True to run for only one step and dump to test
c.set_tstep(U=Umax, dx=dx, T=T, nT=10, nsteps_unit=10, ndumps=10, step_test=False)

# partition is defined after grid because auto setter needs to read grid number to calc npx/npy
# when calling without arguments c.set_partition(), default values are
# nproc_node=48, nnode_max=16, ncell_node=200e3
c.set_partition(nproc_node=16, nnode_max=1)

# set_partition in fact have already enabled job, but here explicit enable it for clarification
# if the job is already enabled, enabling it again simply does nothing
# job is autofilled during first enable based on c.input parallel npx/npy settings
c.job.enable()
c.job.account = "account"

# # jobName is set to case name (folder name) when first enabled by autofill
# c.job.jobname = "tut_sphere"

# # the following two lines are already handled in c.set_partition(...)
# c.job.nodes = 1
# c.job.ntasksPerNode = 16

# write the case input files
c.write()

# # show grid preview
# c.show_grid(gm.center)

# print statistics,
# some need variables not stored in input file so are passed thru args
# it is legal to remove the arg of a stat var and it will be skipped
# c.stat_tstep() is legal, but all stat prints are in 'N/A'
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

# # c.bash() starts the job script by bash, c.sbatch() sends slurm batch job
# c.bash()
# c.sbatch()
