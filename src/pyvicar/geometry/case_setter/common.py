import numpy as np
from pyvicar.geometry.presets import create_sphere, create_cyl_2d, create_plane
from pyvicar.geometry.spanned_2dcurve import Spanned2DCurve
from pyvicar.geometry.trisurface import TriSurface


# pass mesh=None if no surf data is needed (no example for solid, but possible for the memb below)
def append_solid(case, mesh=None):
    case.input.ib.iib = True

    if mesh is None:
        nPoint = 0
        nElem = 0
    else:
        nPoint = mesh.xyz.shape[0]
        nElem = mesh.conn.shape[0]

    case.canonicalBody.nBody = case.canonicalBody.nBody.value + 1
    case.canonicalBody.nBodySolid = case.canonicalBody.nBodySolid.value + 1
    body = case.canonicalBody.bodies.appendnew()
    body.general.bodyType = "unstruc"
    body.general.nPoint = nPoint
    body.general.nElem = nElem

    if not case.unstrucSurface:
        case.unstrucSurface.enable()
        surf = case.unstrucSurface.surfaces.appendnew()
        surf.nPoint = nPoint
        surf.nElem = nElem
        if mesh is not None:
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


# pass mesh=None if no surf data is needed, like IB2 type membrane
def append_membrane(case, mesh=None):
    case.input.ib.iib = True

    if mesh is None:
        nPoint = 0
        nElem = 0
    else:
        nPoint = mesh.xyz.shape[0]
        nElem = mesh.conn.shape[0]

    case.canonicalBody.nBody = case.canonicalBody.nBody.value + 1
    case.canonicalBody.nBodyMembrane = case.canonicalBody.nBodyMembrane.value + 1
    body = case.canonicalBody.bodies.appendnew()
    body.general.bodyType = "unstruc"
    body.general.nPoint = nPoint
    body.general.nElem = nElem

    if not case.unstrucSurface:
        case.unstrucSurface.enable()
        surf = case.unstrucSurface.surfaces.appendnew()
        surf.nPoint = nPoint
        surf.nElem = nElem
        if mesh is not None:
            surf.xyz = mesh.xyz
            surf.conn = mesh.conn

    return body, surf


def append_stl_membrane(case, file, xyz=None):
    mesh = TriSurface.from_stl(file)
    if xyz is not None:
        mesh.xyz.arr += np.array(xyz)
    return append_membrane(case, mesh)


def append_plane(c, uxyz, vxyz, dx, xyz0=None):
    mesh = create_plane(uxyz, vxyz, dx, xyz0)
    return append_membrane(c, mesh)
