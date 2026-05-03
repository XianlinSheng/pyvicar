import pyvicar

# 2. cylinder 2d
# this script generate the case file for a flow past 2D cylinder at Re=200

pyvicar.assert_api_version("1.0.1", "1.1.0")

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

d = 1
U = 1
re = 200
dx = d / 20
T = d / U
Umax = 2 * U

c = Case("tut_cyl2d")

gm = c.create_grid(l0=d, dx=dx, dim2=True, refl=[[2, None], 2])
#                                          ^~~~~~~~~~~~~~~~~~~ 2d pressure spreads in larger distance
#                                                              so needs larger refine region to converge
#                               ^~~~~~~~~ different from example 1, this will create a 2D grid
# 2D case is still using a 3d grid, but only 3 nodes (2 segments) in z direction
# note that 2D is still explicit to solver, and it behaves slightly differently from 3D cases
# [[2, None], 2] means:
#             ^ refine 2*l0 in both y- and y+
#      ^ keep the x+ refine len by default
#   ^ refine 2*l0 length in x- direction from emplacement center (gm.center)
# this list-list notation is used in other arguments too, default values:
# doml=[[20, 5], [20, 20], [20, 20] (in 3d)], * l0 = domain length in each direction from gm.center
# refl=[[1, 2.5], [1, 1], [1, 1] (in 3d)] * l0 = refine box length ...
# grow=[[1.4, 1.02], [1.4, 1.4], [1.4, 1.4] (in 3d)] = growth rate ...
# these defaults create minimal working grid for 3d for efficiency,
# and the above example gives the one for 2d
# if one want to resolve more in the wake, increase doml in x+ and corresponding refl x+, e.g.
# gm = c.create_grid(l0=d, dx=dx, dim2=True, doml=[[None, 10], None], refl=[[2, 6], 2])
# this is easy in 2d but in 3d the need for resources increases much faster
# generally, keep the default growth rate, and make sure aspect ratio is controlled in wake region
# the default 1.02 x+ growth rate and short downstream length are both for a controlled aspect ratio
# because in high-gradient region (lke in wake vortices) high aspect ratio brings instabilities

body, surf = c.append_cyl_2d(d / 2, dx, gm.center)
#                     ^~~~~~ different from example 1
# same, 2D body is a 3D surface, extruded along z and aligned with z layer, check in show_grid() output
# to see only the geometry in detail, using surf.to_trisurf().show(),
# to_trisurf() extracts and rearranges needed info in the config and create a TriSurface geometry object

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
