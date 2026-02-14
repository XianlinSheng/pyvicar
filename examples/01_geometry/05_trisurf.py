import pyvicar as pvc
from pyvicar.geometry.presets import create_sphere
from pyvicar.geometry import TriSurface

# 5. trisurf
# this script generate the case file for a flow past sphere at Re=200, run for one time step,
# where the sphere is described by 2 np arrays, xyz coords and connectivity.
# connectivity is in shape [nelem, 3], [[point idx 1,p2,p3] for elem1,[p1,p2,p3] for elem2, ...]

Case = pvc.case.import_version("~/opt/Vicar3D/common")

d = 1
U = 1
re = 200
dx = d / 20

# this preset gives a TriSurface
trisurf = create_sphere(d / 2, dx, [0, 0, 0])

# this create_sphere(...) is exactly the same function in example 3,
# it always returns the TriSurface in runtime memory,
# but does not write stl file if file=... is not specified

# TriSurface can be directly converted to common structures:
pvpoly = trisurf.to_pyvista()
tmmesh = trisurf.to_trimesh()
trisurf.to_stl("tut_trisurf_stl")  # note .stl will be added automatically
trisurf.to_obj("tut_trisurf_obj")  # note .obj will be added automatically
xyz, conn = trisurf.to_numpy()

# TriSurface is your endpoint if you hold raw data or indirect structures and want to convert
trisurf = TriSurface.from_xyz_conn(xyz, conn)

# IMPORTANT:
# the underlying conn array in TriSurface start idx at 1 by default because Vicar3D starts at 1,
# and it is assumed that in python everyone starts at 0,
# so to_numpy and from_xyz_conn can shift the conn values,
# the above two commands can expand into the following default args
xyz, conn = trisurf.to_numpy(toStartIdx=0)
trisurf = TriSurface.from_xyz_conn(xyz, conn, fromStartIdx=0, toStartIdx=1)
# to_numpy has no fromStartIdx because TriSurface stores this info and it can be checked by
print(f"start at {trisurf.startidx}")

# these are mainly used to show concepts,
# and one can use advanced meshing lib like trimesh/gmsh to create the xyz and conn array

c = Case("tut_trisurf")

gm = c.create_grid(l0=d, dx=dx)

# this emplaces a translated TriSurface,
# .translate(...) modifies the obj inplace, for a new obj, call .copy() first
body, surf = c.append_solid(trisurf.translate(gm.center))


# below is completely the same as example 1/2/3/4

c.set_inlet("x1", [U, 0, 0])
c.set_re(re, U=U, L=d)

c.show_grid(gm.center)

# c.job.enable()
# c.job.jobName = "tut_trisurf"
# c.job.account = "account"

c.write()


# c.mpirun()

# c.sbatch()
