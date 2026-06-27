import pyvicar
from pyvicar.geometry.presets import create_sphere, create_plane
from pyvicar.geometry import TriSurface
import numpy as np

# 10. trisurf
# this script generate the case file for a flow past sphere and a plane membrane at Re=200,
# where both triangular surfaces are described by 2 np arrays, xyz coords and connectivity.
# connectivity is in shape [nelem, 3], [[point idx 1,p2,p3] for elem1,[p1,p2,p3] for elem2, ...]
# in fact, this is the common backend of all the previous solid body examples

pyvicar.assert_api_version("1.0.1", "1.1.0")

Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")

d = 1
U = 1
re = 200
dx = d / 20
T = d / U
Umax = 2 * U
alpha = 5
alpha_rad = np.radians(alpha)

# these presets were used in previous stl examples 5/8 to generate files
# they also directly return a TriSurface in memory
# if file=... is not specified (using default file=None), no file will be created
trisurf_solid = create_sphere(d / 2, dx, [0, 0, 0])

uxyz = np.array([0, -d, 0])
vxyz = np.array([d * np.cos(alpha_rad), 0, -d * np.sin(alpha_rad)])
trisurf_memb = create_plane(uxyz, vxyz, dx, [0, 0, 0])

# TriSurface can be directly converted to common structures:
pvpoly = trisurf_solid.to_pyvista()
tmmesh = trisurf_solid.to_trimesh()
trisurf_solid.to_stl("tut_trisurf_solid_stl")  # note .stl will be added automatically
trisurf_solid.to_obj("tut_trisurf_solid_obj")  # note .obj will be added automatically
xyz, conn = trisurf_solid.to_numpy()

# TriSurface is your endpoint if you hold raw data or indirect structures and want to convert
trisurf_solid = TriSurface.from_xyz_conn(xyz, conn)

# IMPORTANT:
# the underlying conn array in TriSurface start idx at 1 by default because ViCar3D starts at 1,
# and it is assumed that in python everyone starts at 0,
# so to_numpy and from_xyz_conn can shift the conn values,
# the above two commands can expand into the following default args
xyz, conn = trisurf_memb.to_numpy(toStartIdx=0)
trisurf_memb = TriSurface.from_xyz_conn(xyz, conn, fromStartIdx=0, toStartIdx=1)
# to_numpy has no fromStartIdx because TriSurface stores this info and it can be checked by
print(f"start at {trisurf_memb.startidx}")

# these are mainly used to show concepts,
# and one can use advanced meshing lib like trimesh/gmsh to create the xyz and conn array

c = Case("tut_trisurf")

gm = c.create_grid(l0=d, dx=dx)

# this emplaces a translated TriSurface,
# .translate(...) modifies the obj inplace, for a new obj, call .copy() first
body, surf = c.append_solid(trisurf_solid.translate(gm.center - [d, 0, 0]))
# # at here one can configure motion for this body like w=ampz*sin(2*pi*freqz*t):
# # note that the motion is small enough to move inside refined box, for details, see 02_motion/
# body.general.motionType = "forced"
# body.motion.ampz = 0.01
# body.motion.freqz = 0.1

# TriSurface is only surface data and does not distinguish solid or membrane
body, surf = c.append_membrane(trisurf_memb.translate(gm.center + [d, 0, 0]))
# # same on this returned body to configure the membrane, or visualize surface by using surf
# # note that one need to have the x-backend vtk not osmesa to show this on screen
# surf.to_trisurf().show()

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
