import trimesh
import numpy as np
from .trisurface import TriSurface
from .spanned_2dcurve import Spanned2DCurve


def create_sphere(r, dx, xyz=None, file=None):
    n = 0.5 * np.log2((2 * np.pi * r) ** 2 / (20 * dx**2))
    n = max(0, int(np.round(n)))

    mesh = trimesh.creation.icosphere(radius=r, subdivisions=n)
    if xyz is not None:
        mesh.apply_translation(np.array(xyz) - mesh.centroid)

    if file is not None:
        mesh.export(file)
        surf = TriSurface.from_stl(file)
    else:
        surf = TriSurface.from_xyz_conn(mesh.vertices, mesh.faces)

    return surf


def create_cyl_2d(r, dx, xy=None, dz=None, file=None):
    if dz is None:
        dz = dx
    if xy is None:
        xy = [0, 0]
    xy = np.array(xy)
    n = 2 * np.pi * r // dx + 1
    theta = np.arange(0, 2 * np.pi, 2 * np.pi / n)

    x = r * np.cos(theta)
    y = r * np.sin(theta)
    curv = np.vstack([x, y]).T + xy[np.newaxis, :]

    if file is not None:
        Spanned2DCurve.from_2d_xy(curv, 3, dz, cycled=True).to_stl(file)

    return curv
