import pyvicar

# 2. cylinder 2d
# this script generate the case file for a flow past 2D cylinder at Re=200
# note that 2D is typically more difficult to converge and sensitive to parameters in the solver

pyvicar.assert_api_version("1.0.1", "1.1.0")

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

d = 1
U = 1
re = 200
# 2D dz needs to be a clean number (at most 2 significant digits, like 0.015)
dx = d / 50
T = d / U
Umax = 2 * U

c = Case("tut_cyl2d")

gm = c.create_grid(
    l0=d,
    dx=dx,
    dim2=True,
    doml=[[10, 8], 10],
    refl=1.5,
    grow=[[1.05, 1.02], 1.03],
)
# 2D case is still using a 3d grid, but only 3 nodes (2 segments) in z direction
# 2D behaves differently from 3D, use the above mesh

# the list-list notation means
# [[x-, x+], [y-, y+], [z-, z+]], can be broadcasted
# doml=[[10, 8], 10] means domain length is 10*l0 in x- direction from gm.center
#                                            8*l0 in x+
#                                           10*l0 in both y- and y+
# refl=1.5 means refine box length is 1.5*l0 in all direction from gm.center
# grow=[[1.05, 1.02], 1.03] means outside refine box growth rate is 1.05 in x- direction, ...
# default values if not specified:
# doml=[[20, 5], [20, 20], [20, 20] (in 3d)]
# refl=[[1, 2.5], [1, 1], [1, 1] (in 3d)]
# grow=[[1.4, 1.02], [1.4, 1.4], [1.4, 1.4] (in 3d)]
# specify None to use the default, also broadcastable

body, surf = c.append_cyl_2d(d / 2, dx, gm.center)
#                     ^~~~~~ different from example 1
# same, 2D body is a 3D surface, extruded along z and aligned with z layer, check in show_grid() output
# to see only the geometry in detail, using surf.to_trisurf().show(),
# to_trisurf() extracts and rearranges needed info in the config and create a TriSurface geometry object

c.set_inlet("x1", [U, 0, 0])

c.set_re(re, U=U, L=d)

# use divu_tol=1e-4 in 2D, default 1e-6, sometimes cannot converge below and blowup, mechanism not fully clear
c.set_tstep(
    U=Umax, dx=dx, T=T, nT=10, nsteps_unit=10, ndumps=10, step_test=False, divu_tol=1e-4
)

c.set_partition(nproc_node=16, nnode_max=1)

# use 0.1 in 2D, default 1.0, 1.0 sometimes brings divergence, mechanism not fully clear
c.input.hybridization.upwindWeight = 0.1

# in 2D, poisson solver may run into compatibility issue,
# shouldnt keep it iterating and eventually blowup but simply skip the ill-formed tstep,
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
