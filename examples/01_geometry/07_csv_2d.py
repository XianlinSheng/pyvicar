import pyvicar
from pyvicar.geometry.presets import create_cyl_2d

# 7. csv
# this script generate the case file for a flow past 2D cylinder from csv coord columns at Re=200

pyvicar.assert_api_version("1.0.2", "1.1.0")  # csv added in 1.0.2

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

d = 1
U = 1
re = 200
dx = d / 20
T = d / U
Umax = 2 * U

# this creates a 2D cylinder csv file at origin, in real uses one should already have the file somewhere
# simply change the filename extension and program auto detects and decides the format
# in csv it has two columns with header x and y, representing [x1, x2, ..., xn] [y1, y2, ..., yn]
# the cylinder is the closed curve point1-p2-p3-...-pn-p1
# to create one from np arrays, using: pandas.DataFrame({"x": x, "y": y}).to_csv(filename, index=False)
create_cyl_2d(d / 2, dx, [0, 0], file="tut_csv_cyl.csv")

c = Case("tut_csv")

gm = c.create_grid(l0=d, dx=dx, dim2=True, refl=[[3, None], 3])
#                                          ^~~~~~~~~~~~~~~~~~~ remember stricter 2d refine requirement
#                                                              no longer needed starting from d/50
#                                                              typical decent sim. needs at least d/100
#                               ^~~~~~ remember this when creating 2D grid,
#                                      but you can always check for possible mistakes by show_grid()

# this read the csv and emplace at gm.center
body, surf = c.append_csv_solid_2d("tut_csv_cyl.csv", gm.center)
#                    ^~~~ different from example 6

c.set_inlet("x1", [U, 0, 0])

c.set_re(re, U=U, L=d)

c.set_tstep(U=Umax, dx=dx, T=T, nT=10, nsteps_unit=10, ndumps=10, step_test=False)

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
