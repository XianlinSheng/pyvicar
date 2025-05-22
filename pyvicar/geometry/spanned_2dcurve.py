import numpy as np
from pyvicar._datatype import Dataset2D
from .trisurface import TriSurface


class Spanned2DCurve(TriSurface):
    def __init__(
        self,
        xyz: Dataset2D,
        conn: Dataset2D,  # point idx starts from 0
        n2dpoint: int,  # n points as a curve
        n2dseg: int,  # n segments as a curve
        nlayertri: int,  # n triangles in one spanned layer
        nlayer: int,
        nz: int,  # nz = n layers + 1 (one layer is between two z levels)
        cycled: bool,
    ):

        TriSurface.__init__(self, xyz, conn)
        self._n2dpoint = n2dpoint
        self._n2dseg = n2dseg
        self._nlayertri = nlayertri
        self._nlayer = nlayer
        self._nz = nz
        self._cycled = cycled

    @property
    def n2dpoint(self):
        return self._n2dpoint

    @property
    def n2dseg(self):
        return self._n2dseg

    @property
    def nlayertri(self):
        return self._nlayertri

    @property
    def nlayer(self):
        return self._nlayer

    @property
    def nz(self):
        return self._nz

    @property
    def cycled(self):
        return self._cycled

    def from_2d_xy(
        xy: np.ndarray, nz: int, dz: float, cycled: bool = False, startIdx: int = 1
    ):
        if np.issubdtype(xy.dtype, np.integer):
            xy = np.array(xy, dtype=float)

        if not np.issubdtype(xy.dtype, np.floating):
            raise TypeError(
                f"Expected floatable (int/float) dtype for xy list, but encountered {repr(xy)}"
            )

        if len(xy.shape) != 2 or xy.shape[1] != 2:
            raise ValueError(
                f"Expected n*2 shape for xy2 list, but encountered {xy.shape}"
            )

        npoint = xy.shape[0]
        nseg = npoint if cycled else npoint - 1

        zs = []
        for zi in range(nz):
            z = zi * dz
            zs.append(np.ones(xy.shape[0]) * z)
        zs = np.concatenate(zs)
        # repeat xy for nz times
        xys = np.tile(xy, (nz, 1))
        xyzs = np.concatenate((xys, zs[:, np.newaxis]), axis=1)

        nlayer = nz - 1
        nlayertri = nseg * 2

        # construct one layer first
        conn = np.zeros((nlayertri, 3), dtype=int)

        #  ...  ... + zi * npoint
        #   v    v
        # D +----+ C
        #   |\   |
        #   | \  |
        #   |  \ |
        #   |   \|
        # A +----+ B
        #   ^    ^
        #   i   i+1

        A = np.arange(npoint - 1, dtype=int)
        B = np.arange(1, npoint, dtype=int)
        if cycled:
            A = np.concatenate([A, npoint - 1], dtype=int)
            B = np.concatenate([B, 0], dtype=int)

        C = B + npoint
        D = A + npoint

        # first node for tris
        conn[0::2, 0] = A
        conn[1::2, 0] = B

        # second node for tris
        conn[0::2, 1] = B
        conn[1::2, 1] = C

        # third node for tris
        conn[0::2, 2] = D
        conn[1::2, 2] = D

        # repeat and offset for the remaining layers
        conns = []
        for zi in range(nz - 1):
            conns.append(conn + npoint * zi)

        conns = np.vstack(conns)

        conns += startIdx

        return Spanned2DCurve(
            xyz=Dataset2D(xyzs, startIdx=startIdx),
            conn=Dataset2D(conns, startIdx=startIdx),
            n2dpoint=npoint,
            n2dseg=nseg,
            nlayertri=nlayertri,
            nlayer=nlayer,
            nz=nz,
            cycled=cycled,
        )
