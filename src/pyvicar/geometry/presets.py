import trimesh
import numpy as np
import pandas as pd
from pathlib import Path
from .trisurface import TriSurface
from .spanned_2dcurve import Spanned2DCurve


def create_sphere(r, dx, xyz=None, file=None):
    n = 0.5 * np.log2((2 * np.pi * r) ** 2 / (20 * dx**2))
    n = max(0, int(np.round(n)))

    mesh = trimesh.creation.icosphere(radius=r, subdivisions=n)
    if xyz is not None:
        mesh.apply_translation(np.array(xyz) - mesh.centroid)

    if file is not None:
        suffix = Path(file).suffix
        match suffix:
            case ".stl":
                mesh.export(file)
            case _:
                raise RuntimeError(
                    f"Unrecognized output file format, supports [.stl], got {suffix}"
                )

    # THIS MUST BE PLACED AFTER EXPORT, TRISURFACE DOES ZERO COPY AND MODIFIES ARRAY
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
        suffix = Path(file).suffix
        match suffix:
            case ".npz":
                np.savez(file, xy=curv)
            case ".csv":
                df = pd.DataFrame({"x": curv[:, 0], "y": curv[:, 1]})
                df.to_csv(file, index=False)
            case _:
                raise RuntimeError(
                    f"Unrecognized output file format, supports [.npz, .csv], got {suffix}"
                )

    return curv


def create_plane(uxyz, vxyz, dx, xyz0=None, file=None):
    uxyz = np.asarray(uxyz)
    vxyz = np.asarray(vxyz)

    lu = np.linalg.norm(uxyz)
    lv = np.linalg.norm(vxyz)

    nu = int(np.ceil(lu / dx))
    nv = int(np.ceil(lv / dx))

    us = np.linspace(0, lu, nu + 1, endpoint=True)
    ws = np.zeros_like(us)
    uws = np.stack((us, ws)).T
    uwv, conn = Spanned2DCurve.from_2d_xy(uws, nv + 1, lv / nv, cycled=False).to_numpy()

    A = np.hstack((uxyz[:, None] / lu, vxyz[:, None] / lv))

    uv = uwv[:, [0, 2]]
    xyz = np.einsum("ij,kj->ki", A, uv)

    if xyz0 is not None:
        xyz += np.asarray(xyz0)[None, :]

    surf = TriSurface.from_xyz_conn(xyz, conn)

    if file is not None:
        suffix = Path(file).suffix
        match suffix:
            case ".stl":
                surf.to_stl(Path(file).stem)
            case _:
                raise RuntimeError(
                    f"Unrecognized output file format, supports [.stl], got {suffix}"
                )

    return surf


def create_plane_2d(vec, dx, xy0=None, file=None):
    vec = np.asarray(vec)

    l = np.linalg.norm(vec)

    n = int(np.ceil(l / dx))

    i = np.arange(n + 1)
    if xy0 is None:
        xy0 = [0, 0]
    xy0 = np.asarray(xy0)

    curv = xy0[np.newaxis, :] + i[:, np.newaxis] * vec / n

    if file is not None:
        suffix = Path(file).suffix
        match suffix:
            case ".npz":
                np.savez(file, xy=curv)
            case ".csv":
                df = pd.DataFrame({"x": curv[:, 0], "y": curv[:, 1]})
                df.to_csv(file, index=False)
            case _:
                raise RuntimeError(
                    f"Unrecognized output file format, supports [.npz, .csv], got {suffix}"
                )

    return curv
