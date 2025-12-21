import numpy as np
import pyvista as pv
import trimesh
from pyvicar._datatype import Dataset2D
from .stl_reader import read_stl


class TriSurface:
    def __init__(self, xyz: Dataset2D, conn: Dataset2D):
        self._xyz = xyz
        self._conn = conn
        self._nPoint = xyz.shape[0]
        self._nElem = conn.shape[0]

    @property
    def xyz(self):
        return self._xyz

    @property
    def conn(self):
        return self._conn

    @property
    def nPoint(self):
        return self._nPoint

    @property
    def nElem(self):
        return self._nElem

    @property
    def startidx(self):
        return self._xyz.startidx

    def copy(self):
        return TriSurface(self._xyz.copy(), self._conn.copy())

    def translate(self, dxyz):
        self._xyz.arr += np.array(dxyz)
        return self

    def show(self):
        self.to_pyvista().plot(show_edges=True, color="lightblue")

    def to_pyvista(self):
        points = self._xyz.arr
        faces = self._conn.arr - self._conn.startidx

        # pyvista takes: [3, i0, i1, i2, 3, i0, i1, i2, ...]
        faces_pv = np.hstack([np.full((faces.shape[0], 1), 3), faces]).ravel()

        return pv.PolyData(points, faces_pv)

    def to_trimesh(self):
        return trimesh.Trimesh(
            vertices=self._xyz.arr, faces=(self._conn.arr - self._xyz.startidx)
        )

    def to_numpy(self, toStartIdx: int = 0):
        return self._xyz.arr, self._conn.arr + (toStartIdx - self._xyz.startidx)

    def to_stl(self, filename):
        self.to_trimesh().export(f"{filename}.stl")

    def to_obj(self, filename):
        self.to_trimesh().export(f"{filename}.obj")

    def from_xyz_conn(
        xyz: np.ndarray, conn: np.ndarray, fromStartIdx: int = 0, toStartIdx: int = 1
    ):
        if np.issubdtype(xyz.dtype, np.integer):
            xyz = np.array(xyz, dtype=float)

        if not np.issubdtype(xyz.dtype, np.floating):
            raise TypeError(
                f"Expected floatable (int/float) dtype for xyz list, but encountered {repr(xyz)}"
            )

        if not np.issubdtype(conn.dtype, np.integer):
            raise TypeError(
                f"Expected integer for conn list, but encountered {repr(conn)}"
            )

        if len(xyz.shape) != 2 or xyz.shape[1] != 3:
            raise ValueError(
                f"Expected n*3 shape for xyz list, but encountered {xyz.shape}"
            )

        if len(conn.shape) != 2 or conn.shape[1] != 3:
            raise ValueError(
                f"Expected n*3 shape for conn list, but encountered {conn.shape}"
            )

        pimin = np.min(conn)
        pimax = np.max(conn)
        if pimin < fromStartIdx or pimax > fromStartIdx + xyz.shape[0]:
            raise ValueError(
                f"Referred to a point out of index: xyz defines indexes [{fromStartIdx}, {fromStartIdx + xyz.shape[0] - 1}], but referred range is [{pimin}, {pimax}]"
            )

        conn += toStartIdx - fromStartIdx

        return TriSurface(
            xyz=Dataset2D(xyz, startIdx=toStartIdx),
            conn=Dataset2D(conn, startIdx=toStartIdx),
        )

    def from_stl(path, tol=1e-10, startIdx=1):
        xyz, conn, bounding_box = read_stl(path, tol)

        conn += startIdx

        return TriSurface(
            xyz=Dataset2D(xyz, startIdx=startIdx),
            conn=Dataset2D(conn, startIdx=startIdx),
        )

    def from_obj(path, startIdx=1):
        mesh = trimesh.load(path)
        return TriSurface(
            Dataset2D(mesh.vertices, startIdx=startIdx),
            Dataset2D(mesh.faces + startIdx, startIdx=startIdx),
        )

    def from_npz(path, fromStartIdx=0, toStartIdx=1):
        data = np.load(path)
        return TriSurface.from_xyz_conn(
            data["xyz"], data["conn"], fromStartIdx, toStartIdx
        )

    def from_unstruc(surf):
        return TriSurface.from_xyz_conn(
            surf.xyz.value.arr,
            surf.conn.value.arr,
            surf.xyz.value.startidx,
            surf.xyz.value.startidx,
        )
