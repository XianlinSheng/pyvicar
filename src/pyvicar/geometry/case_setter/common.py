import numpy as np
from pyvicar.geometry.presets import create_sphere, create_cyl_2d
from pyvicar.geometry.spanned_2dcurve import Spanned2DCurve
from pyvicar.geometry.trisurface import TriSurface


def append_solid(case, mesh):
    case.input.ib.iib = True

    case.canonicalBody.nBody = case.canonicalBody.nBody.value + 1
    case.canonicalBody.nBodySolid = case.canonicalBody.nBodySolid.value + 1
    body = case.canonicalBody.bodies.appendnew()
    body.general.bodyType = "unstruc"
    body.general.nPoint = mesh.xyz.shape[0]
    body.general.nElem = mesh.conn.shape[0]

    if not case.unstrucSurface:
        case.unstrucSurface.enable()
        surf = case.unstrucSurface.surfaces.appendnew()
        surf.nPoint = mesh.xyz.shape[0]
        surf.nElem = mesh.conn.shape[0]
        surf.xyz = mesh.xyz
        surf.conn = mesh.conn

    return body, surf


# solid is a closed loop, so default cycled
def append_solid_2d(case, curv, cycled=True):
    nz = case.input.domain.nz.value
    zout = case.input.domain.zout.value
    dz = zout / (nz - 1)

    mesh = Spanned2DCurve.from_2d_xy(curv, nz, dz, cycled=cycled)

    body, surf = append_solid(case, mesh)
    body.general.bodyDim = 2

    return body, surf


def append_sphere(case, r, dx, xyz):
    mesh = create_sphere(r, dx, xyz)
    return append_solid(case, mesh)


def append_cyl_2d(case, r, dx, xy):
    curv = create_cyl_2d(r, dx, xy)
    return append_solid_2d(case, curv)


def append_stl_solid(case, file, xyz=None):
    mesh = TriSurface.from_stl(file)
    if xyz is not None:
        mesh.xyz.arr += np.array(xyz)
    return append_solid(case, mesh)


def append_npz_solid_2d(case, file, xy=None):
    curv = np.load(file)["xy"]
    if xy is not None:
        curv += np.array(xy)[np.newaxis, :]
    return append_solid_2d(case, curv)
